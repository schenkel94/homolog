import re
import urllib.parse
import pandas as pd
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from pathlib import Path
from datetime import datetime

BASE_URL_TEMPLATE = "https://{}.inhire.app/vagas"
KEYWORDS = ["analista de dados", "data analyst", "analista de negocios", "business analyst", "dataviz", "dados"]

# Configurações de paralelismo
MAX_CONCURRENT_COMPANIES = 5  # Processa 5 empresas simultaneamente
MAX_CONCURRENT_JOBS = 3       # Processa 3 vagas por empresa simultaneamente

# Tempo de espera
WAIT_FOR_JOBS_TIMEOUT = 15000  # 15 segundos


async def extract_job_details(context, job_info, company, job_number, total_jobs, debug_dir):
    """
    Extrai detalhes de uma vaga específica (async)
    """
    print(f"    [{job_number}/{total_jobs}] Acessando vaga...")
    
    job_page = None
    try:
        # Abre a vaga em uma nova página
        job_page = await context.new_page()
        await job_page.goto(job_info['url'], timeout=60000)
        await job_page.wait_for_load_state("networkidle")
        await job_page.wait_for_timeout(2000)
        
        # Pega HTML da vaga
        job_html = await job_page.content()
        
        # Salva para debug
        async with asyncio.Lock():  # Evita conflito ao salvar
            with open(debug_dir / f"{company}_job_{job_number}.html", "w", encoding="utf-8") as f:
                f.write(job_html)
        
        # Parse dos detalhes
        job_soup = BeautifulSoup(job_html, "html.parser")
        
        # ===== EXTRAÇÃO DE INFORMAÇÕES =====
        
        # Título
        title = None
        title_elem = job_soup.find(['h1', 'h2'])
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            title_tag = job_soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
        
        if not title:
            title = job_info['title_preview']
        
        # Localidade
        location = "Não informado"
        location_patterns = [
            r"Remota|Remoto",
            r"Remote",
            r"Home Office",
            r"Presencial"
        ]
        
        page_text = job_soup.get_text(separator=" ", strip=True)
        for pattern in location_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                location = match.group(0)
                break
        
        # Descrição
        description = ""
        meta_desc = job_soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content']
        
        if not description:
            paragraphs = job_soup.find_all('p', limit=3)
            description = " ".join([p.get_text(strip=True) for p in paragraphs])
        
        if len(description) > 500:
            description = description[:500] + "..."
        
        # Requisitos
        requirements = []
        req_keywords = ['requisito', 'requirement', 'qualificação', 'qualification']
        
        for keyword in req_keywords:
            section = job_soup.find(string=re.compile(keyword, re.IGNORECASE))
            if section:
                parent = section.find_parent()
                if parent:
                    ul = parent.find_next('ul')
                    if ul:
                        items = ul.find_all('li')
                        requirements = [item.get_text(strip=True) for item in items[:5]]
                        break
        
        requirements_text = " | ".join(requirements) if requirements else "Não informado"
        
        # Monta dados
        job_data = {
            "empresa": company.upper(),
            "nome_vaga": title,
            "localidade": location,
            "descricao": description,
            "requisitos": requirements_text,
            "link": job_info['url'],
            "data_etl": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"    ✅ [{job_number}/{total_jobs}] {title[:50]}")
        
        return job_data
    
    except Exception as e:
        print(f"    ❌ [{job_number}/{total_jobs}] Erro: {str(e)[:100]}")
        return None
    
    finally:
        if job_page:
            await job_page.close()


async def fetch_jobs_with_details(browser, company, semaphore):
    """
    Busca vagas de uma empresa e extrai detalhes (async com semáforo)
    """
    async with semaphore:  # Limita concorrência
        url = BASE_URL_TEMPLATE.format(company)
        print(f"\n  🌐 [{company.upper()}] Acessando: {url}")
        
        jobs_data = []
        context = None
        page = None
        
        try:
            context = await browser.new_context()
            page = await context.new_page()
            
            # Acessa a página
            await page.goto(url, timeout=60000)
            print(f"  ⏳ [{company.upper()}] Aguardando página carregar...")
            
            await page.wait_for_load_state("networkidle")
            
            # ===== AGUARDA VAGAS APARECEREM =====
            print(f"  ⏳ [{company.upper()}] Aguardando vagas...")
            
            vaga_apareceu = False
            seletores_possiveis = [
                "a[href*='/vagas/']",
                "a[href*='analista']",
                "[class*='job']",
                "[class*='vaga']",
                "[class*='card']",
            ]
            
            for seletor in seletores_possiveis:
                try:
                    await page.wait_for_selector(seletor, timeout=WAIT_FOR_JOBS_TIMEOUT)
                    print(f"  ✅ [{company.upper()}] Vagas carregadas!")
                    vaga_apareceu = True
                    break
                except PlaywrightTimeout:
                    continue
            
            if not vaga_apareceu:
                print(f"  ⚠️  [{company.upper()}] Timeout aguardando vagas")
            
            await page.wait_for_timeout(3000)
            
            # Scroll
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Pega HTML
            html = await page.content()
            
            # Salva HTML
            debug_dir = Path("debug_html")
            debug_dir.mkdir(exist_ok=True)
            with open(debug_dir / f"{company}_listing.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            # Parse
            soup = BeautifulSoup(html, "html.parser")
            
            # Encontra links
            job_links = []
            links = soup.find_all("a", href=re.compile(r"/vagas/[a-f0-9-]+"))
            print(f"  🔍 [{company.upper()}] Encontrados {len(links)} links de vagas")
            
            for link in links:
                text = link.get_text(separator=" ", strip=True).lower()
                href = link.get("href", "")
                
                if any(keyword.lower() in text for keyword in KEYWORDS):
                    if href.startswith("http"):
                        full_url = href
                    else:
                        full_url = urllib.parse.urljoin(url, href)
                    
                    job_links.append({
                        'url': full_url,
                        'title_preview': text[:80]
                    })
            
            print(f"  ✅ [{company.upper()}] {len(job_links)} vagas com keywords encontradas")
            
            if not job_links:
                page_text = soup.get_text(separator=" ", strip=True)
                for keyword in KEYWORDS:
                    if keyword.lower() in page_text.lower():
                        print(f"  ⚠️  [{company.upper()}] Keyword '{keyword}' encontrada mas sem link")
            
            # ===== PROCESSA VAGAS EM PARALELO =====
            if job_links:
                print(f"  🚀 [{company.upper()}] Processando {len(job_links)} vagas em paralelo...")
                
                # Cria semáforo para limitar vagas concorrentes
                job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)
                
                # Cria tasks para todas as vagas
                tasks = []
                for i, job_info in enumerate(job_links, 1):
                    task = asyncio.create_task(
                        extract_job_details_with_semaphore(
                            context, job_info, company, i, len(job_links), debug_dir, job_semaphore
                        )
                    )
                    tasks.append(task)
                
                # Aguarda todas as tasks
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filtra resultados válidos
                jobs_data = [r for r in results if r is not None and not isinstance(r, Exception)]
                
                print(f"  ✅ [{company.upper()}] {len(jobs_data)} vagas extraídas com sucesso!")
        
        except Exception as e:
            print(f"  ❌ [{company.upper()}] Erro: {str(e)[:100]}")
        
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
        
        return jobs_data


async def extract_job_details_with_semaphore(context, job_info, company, job_number, total_jobs, debug_dir, semaphore):
    """
    Wrapper com semáforo para controlar concorrência de vagas
    """
    async with semaphore:
        return await extract_job_details(context, job_info, company, job_number, total_jobs, debug_dir)


async def main_async():
    """
    Função principal async que processa empresas em paralelo
    """
    print("🚀 INICIANDO BUSCA PARALELA DE VAGAS\n")
    print("=" * 80)
    print(f"⚡ Processando {MAX_CONCURRENT_COMPANIES} empresas simultaneamente")
    print(f"⚡ Processando {MAX_CONCURRENT_JOBS} vagas por empresa simultaneamente")
    print("=" * 80)
    
    # Lê empresas
    companies_file = Path("companies.txt")
    
    if not companies_file.exists():
        print("❌ Arquivo companies.txt não encontrado!")
        print("   Criando arquivo de exemplo...")
        with open("companies.txt", "w", encoding="utf-8") as f:
            f.write("sympla\n")
        print("✅ Arquivo criado. Execute novamente.\n")
        return
    
    with open("companies.txt", "r", encoding="utf-8") as f:
        companies = [line.strip() for line in f if line.strip()]
    
    print(f"\n📊 Empresas: {len(companies)}")
    print(f"🔍 Keywords: {', '.join(KEYWORDS)}\n")
    print("=" * 80)
    
    start_time = datetime.now()
    
    async with async_playwright() as p:
        # Lança browser uma vez (compartilhado)
        browser = await p.chromium.launch(headless=True)  # headless=True para performance
        
        try:
            # Cria semáforo para limitar empresas concorrentes
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_COMPANIES)
            
            # Cria tasks para todas as empresas
            tasks = [
                fetch_jobs_with_details(browser, company, semaphore)
                for company in companies
            ]
            
            # Executa todas em paralelo
            print(f"\n🚀 Iniciando processamento paralelo de {len(companies)} empresas...\n")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolida resultados
            all_jobs = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"\n❌ Empresa {companies[i]} falhou: {result}")
                elif result:
                    all_jobs.extend(result)
        
        finally:
            await browser.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print(f"📊 RESULTADO FINAL: {len(all_jobs)} vagas")
    print(f"⏱️  Tempo total: {duration:.1f} segundos ({duration/60:.1f} minutos)")
    print(f"⚡ Velocidade: {len(companies)/duration*60:.1f} empresas/minuto")
    print("=" * 80)
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df = df.drop_duplicates(subset=["link"])
        
        print(f"\n📋 Após remover duplicatas: {len(df)} vagas\n")
        print(df[["empresa", "nome_vaga", "localidade"]].to_string(index=False))
        
        # Salva resultados
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"vagas_{timestamp}.csv"
        excel_file = f"vagas_{timestamp}.xlsx"
        
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        df.to_excel(excel_file, index=False, engine="openpyxl")
        
        print(f"\n✅ Resultados salvos:")
        print(f"   📄 {csv_file}")
        print(f"   📊 {excel_file}")
        print(f"   🔍 debug_html/")
        
        # Estatísticas
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total de vagas: {len(df)}")
        print(f"   Empresas com vagas: {df['empresa'].nunique()}")
        print(f"   Média: {len(df)/df['empresa'].nunique():.1f} vagas/empresa")
        print(f"\n   Vagas por empresa:")
        print(df['empresa'].value_counts().to_string())
        print(f"\n   Vagas por localidade:")
        print(df['localidade'].value_counts().to_string())
    
    else:
        print("\n⚠️  Nenhuma vaga encontrada!")


def main():
    """
    Entry point que roda a versão async
    """
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
