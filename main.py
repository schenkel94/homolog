import re
import urllib.parse
import pandas as pd
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pathlib import Path

BASE_URL_TEMPLATE = "https://{}.inhire.app/vagas"
KEYWORDS = ["analista de dados", "data analyst", "analista de negocios", "business analyst", "dataviz", "dados"]

# Tempo de espera para vagas carregarem
WAIT_FOR_JOBS_TIMEOUT = 15000  # 15 segundos


def fetch_jobs_with_details(company):
    """
    Busca vagas E clica em cada uma para extrair detalhes.
    
    Returns:
        list: Lista de dicionários com informações das vagas
    """
    url = BASE_URL_TEMPLATE.format(company)
    print(f"  🌐 Acessando: {url}")
    
    jobs_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #isso faz abrir o navegador ou nao
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Acessa a página
            page.goto(url, timeout=60000)
            print(f"  ⏳ Aguardando página carregar...")
            
            # Aguarda network idle
            page.wait_for_load_state("networkidle")
            
            # ===== AGUARDA VAGAS APARECEREM =====
            # Tenta aguardar por diferentes seletores comuns
            print(f"  ⏳ Aguardando vagas aparecerem...")
            
            vaga_apareceu = False
            seletores_possiveis = [
                "a[href*='/vagas/']",  # Links com /vagas/
                "a[href*='analista']",  # Links com analista
                "[class*='job']",      # Elementos com 'job' na classe
                "[class*='vaga']",     # Elementos com 'vaga' na classe
                "[class*='card']",     # Cards
            ]
            
            for seletor in seletores_possiveis:
                try:
                    page.wait_for_selector(seletor, timeout=WAIT_FOR_JOBS_TIMEOUT)
                    print(f"  ✅ Vagas carregadas! (seletor: {seletor})")
                    vaga_apareceu = True
                    break
                except PlaywrightTimeout:
                    continue
            
            if not vaga_apareceu:
                print(f"  ⚠️  Timeout aguardando vagas. Continuando mesmo assim...")
            
            # Aguarda mais um pouco para garantir
            page.wait_for_timeout(3000)
            
            # Scroll para garantir que tudo carregou (lazy loading)
            print(f"  📜 Fazendo scroll na página...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
            # Pega HTML final
            html = page.content()
            
            # Salva HTML para debug
            debug_dir = Path("debug_html")
            debug_dir.mkdir(exist_ok=True)
            with open(debug_dir / f"{company}_listing.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  💾 HTML da listagem salvo: debug_html/{company}_listing.html")
            
            # Parse da listagem
            soup = BeautifulSoup(html, "html.parser")
            
            # Encontra todos os links de vagas
            job_links = []
            
            # Estratégia 1: Links com /vagas/[uuid]
            links = soup.find_all("a", href=re.compile(r"/vagas/[a-f0-9-]+"))
            print(f"  🔍 Encontrados {len(links)} links de vagas")
            
            for link in links:
                text = link.get_text(separator=" ", strip=True).lower()
                href = link.get("href", "")
                
                # Verifica se contém keyword
                if any(keyword.lower() in text for keyword in KEYWORDS):
                    # Monta URL completa
                    if href.startswith("http"):
                        full_url = href
                    else:
                        full_url = urllib.parse.urljoin(url, href)
                    
                    job_links.append({
                        'url': full_url,
                        'title_preview': text[:80]
                    })
                    print(f"  ✅ Vaga encontrada: {text[:60]}...")
            
            if not job_links:
                print(f"  ⚠️  Nenhuma vaga com keywords encontrada na listagem")
                
                # Debug: mostra o que tem na página
                page_text = soup.get_text(separator=" ", strip=True)
                print(f"  🔍 Texto da página (primeiros 500 chars):")
                print(f"     {page_text[:500]}")
                
                # Verifica se keywords aparecem
                for keyword in KEYWORDS:
                    if keyword.lower() in page_text.lower():
                        print(f"  ✅ Keyword '{keyword}' ENCONTRADA no texto")
            
            # ===== CLICA EM CADA VAGA PARA EXTRAIR DETALHES =====
            print(f"\n  🖱️  Extraindo detalhes de {len(job_links)} vagas...")
            
            for i, job_info in enumerate(job_links, 1):
                print(f"\n  [{i}/{len(job_links)}] Acessando vaga...")
                
                try:
                    # Abre a vaga em uma nova página
                    job_page = context.new_page()
                    job_page.goto(job_info['url'], timeout=60000)
                    job_page.wait_for_load_state("networkidle")
                    job_page.wait_for_timeout(2000)
                    
                    # Pega HTML da vaga
                    job_html = job_page.content()
                    
                    # Salva para debug
                    with open(debug_dir / f"{company}_job_{i}.html", "w", encoding="utf-8") as f:
                        f.write(job_html)
                    
                    # Parse dos detalhes
                    job_soup = BeautifulSoup(job_html, "html.parser")
                    
                    # ===== EXTRAÇÃO DE INFORMAÇÕES =====
                    
                    # Título (procura em h1, h2, ou título da página)
                    title = None
                    title_elem = job_soup.find(['h1', 'h2'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    else:
                        # Tenta pegar do title da página
                        title_tag = job_soup.find('title')
                        if title_tag:
                            title = title_tag.get_text(strip=True)
                    
                    if not title:
                        title = job_info['title_preview']
                    
                    # Localidade (procura por "Remota", "Remoto", etc.)
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
                    
                    # Descrição (primeiros parágrafos ou div principal)
                    description = ""
                    
                    # Tenta meta description
                    meta_desc = job_soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        description = meta_desc['content']
                    
                    # Se não tem, pega primeiros parágrafos
                    if not description:
                        paragraphs = job_soup.find_all('p', limit=3)
                        description = " ".join([p.get_text(strip=True) for p in paragraphs])
                    
                    # Limita tamanho
                    if len(description) > 500:
                        description = description[:500] + "..."
                    
                    # Requisitos (procura por listas ou seções)
                    requirements = []
                    req_keywords = ['requisito', 'requirement', 'qualificação', 'qualification']
                    
                    for keyword in req_keywords:
                        section = job_soup.find(string=re.compile(keyword, re.IGNORECASE))
                        if section:
                            parent = section.find_parent()
                            if parent:
                                # Procura listas próximas
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
                    
                    jobs_data.append(job_data)
                    
                    print(f"  ✅ Título: {title[:60]}")
                    print(f"  📍 Local: {location}")
                    print(f"  🔗 Link: {job_info['url'][:60]}...")
                    
                    # Fecha a página da vaga
                    job_page.close()
                    
                    # Delay entre vagas
                    time.sleep(1)
                
                except Exception as e:
                    print(f"  ❌ Erro ao processar vaga: {str(e)[:100]}")
                    continue
        
        finally:
            browser.close()
    
    return jobs_data


def main():
    print("🚀 INICIANDO BUSCA DETALHADA DE VAGAS\n")
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
    
    print(f"📊 Empresas: {len(companies)}")
    print(f"🔍 Keywords: {', '.join(KEYWORDS)}\n")
    print("=" * 80)
    
    all_jobs = []
    
    for i, company in enumerate(companies, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(companies)}] 🏢 {company.upper()}")
        print(f"{'='*80}")
        
        try:
            jobs = fetch_jobs_with_details(company)
            
            if jobs:
                print(f"\n  ✅ {len(jobs)} vagas extraídas com detalhes!")
                all_jobs.extend(jobs)
            else:
                print(f"\n  ⚠️  Nenhuma vaga encontrada")
        
        except Exception as e:
            print(f"\n  ❌ Erro: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"📊 RESULTADO FINAL: {len(all_jobs)} vagas")
    print("=" * 80)
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        
        # Remove duplicatas por link
        df = df.drop_duplicates(subset=["link"])
        
        print(f"\n📋 Após remover duplicatas: {len(df)} vagas\n")
        
        # Mostra resumo
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
        print(f"   🔍 debug_html/ (HTMLs para análise)")
        
        # Estatísticas
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total de vagas: {len(df)}")
        print(f"   Empresas: {df['empresa'].nunique()}")
        print(f"\n   Vagas por empresa:")
        print(df['empresa'].value_counts().to_string())
        
        print(f"\n   Vagas por localidade:")
        print(df['localidade'].value_counts().to_string())
    
    else:
        print("\n⚠️  Nenhuma vaga encontrada!")
        print("\n💡 Dicas:")
        print("   1. Verifique debug_html/")
        print("   2. Abra os HTMLs e procure as vagas manualmente")
        print("   3. Veja se as keywords estão corretas")
        print("   4. Tente aumentar WAIT_FOR_JOBS_TIMEOUT")


if __name__ == "__main__":
    main()
