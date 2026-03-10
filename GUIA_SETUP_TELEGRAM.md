# 📱 Guia Completo: Setup de Alertas no Telegram e Escalabilidade

## 🎯 Objetivo
Este guia complementa o Jupyter Notebook `monitor_vagas_inhire.ipynb` e ensina como:
1. Configurar alertas automáticos no Telegram
2. Agendar execução automática
3. Escalar a solução para monitoramento contínuo
4. Técnicas avançadas de descoberta de vagas

---

## 📱 PARTE 1: Configurando Telegram Bot

### Passo 1: Criar o Bot

1. Abra o Telegram e procure por `@BotFather`
2. Envie o comando `/newbot`
3. Siga as instruções:
   - Nome do bot: `Monitor Vagas InHire`
   - Username: `seu_nome_vagas_bot` (deve terminar em `_bot`)
4. **IMPORTANTE**: Copie o TOKEN fornecido (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Passo 2: Obter seu Chat ID

**Método 1 - Via Bot:**
1. Envie qualquer mensagem para o seu bot
2. Acesse no navegador:
   ```
   https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
   ```
3. Procure por `"chat":{"id":123456789}` e copie o número

**Método 2 - Via Python:**
```python
import requests

TOKEN = "seu_token_aqui"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

for update in response['result']:
    print(f"Chat ID: {update['message']['chat']['id']}")
```

### Passo 3: Configurar no Notebook

Abra o notebook e na célula de configuração do Telegram:
```python
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Seu token
TELEGRAM_CHAT_ID = "123456789"  # Seu chat ID
```

### Passo 4: Testar

Execute a célula de teste:
```python
enviar_alerta_telegram(df_vagas)
```

Se receber mensagem no Telegram: ✅ Configurado corretamente!

---

## ⏰ PARTE 2: Agendamento Automático

### Opção A: Windows Task Scheduler

1. **Criar script .bat:**
   ```batch
   @echo off
   cd C:\caminho\do\seu\projeto
   C:\Users\SeuUsuario\Anaconda3\python.exe -m jupyter nbconvert --to notebook --execute monitor_vagas_inhire.ipynb
   ```

2. **Agendar:**
   - Abra Task Scheduler (Agendador de Tarefas)
   - Criar Tarefa Básica
   - Nome: "Monitor Vagas InHire"
   - Gatilho: Diariamente às 09:00
   - Ação: Iniciar programa → Selecione o arquivo .bat

### Opção B: Linux/Mac (Cron)

1. **Abrir crontab:**
   ```bash
   crontab -e
   ```

2. **Adicionar linha:**
   ```bash
   # Rodar todo dia às 9h
   0 9 * * * cd /caminho/do/projeto && /caminho/do/python -m jupyter nbconvert --to notebook --execute monitor_vagas_inhire.ipynb
   
   # OU usando conda
   0 9 * * * /caminho/do/conda run -n base jupyter nbconvert --to notebook --execute /caminho/completo/monitor_vagas_inhire.ipynb
   ```

3. **Verificar:**
   ```bash
   crontab -l  # Lista tarefas agendadas
   ```

### Opção C: GitHub Actions (Nuvem - Grátis)

1. **Criar arquivo `.github/workflows/monitor.yml`:**
```yaml
name: Monitor Vagas InHire

on:
  schedule:
    - cron: '0 12 * * *'  # UTC - ajuste para seu fuso
  workflow_dispatch:  # Permite execução manual

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install jupyter requests beautifulsoup4 pandas lxml tqdm fake-useragent python-telegram-bot
    
    - name: Run notebook
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: |
        jupyter nbconvert --to notebook --execute monitor_vagas_inhire.ipynb
```

2. **Adicionar secrets no GitHub:**
   - Settings → Secrets → New repository secret
   - Adicione `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`

3. **Vantagens:**
   - Roda na nuvem (não precisa deixar PC ligado)
   - Grátis até 2000 minutos/mês
   - Logs automáticos

---

## 🚀 PARTE 3: Escalando a Solução

### 3.1 Banco de Dados para Histórico

**Por que?** Evitar alertas duplicados e analisar tendências.

```python
import sqlite3
from datetime import datetime

# Conectar ao banco
conn = sqlite3.connect('vagas_historico.db')

# Criar tabela (execute apenas uma vez)
conn.execute('''
CREATE TABLE IF NOT EXISTS vagas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa TEXT,
    titulo TEXT,
    link TEXT UNIQUE,
    data_publicacao TEXT,
    data_descoberta TEXT,
    enviado_telegram BOOLEAN DEFAULT 0
)
''')

# Salvar novas vagas
def salvar_vagas_novas(df_vagas):
    novas = []
    for _, row in df_vagas.iterrows():
        try:
            conn.execute('''
                INSERT INTO vagas (empresa, titulo, link, data_publicacao, data_descoberta)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['Empresa'], row['Título da Vaga'], row['Link Direto'], 
                  row['Data de Publicação'], datetime.now().isoformat()))
            novas.append(row)
        except sqlite3.IntegrityError:
            # Link já existe no banco (vaga já foi descoberta antes)
            pass
    
    conn.commit()
    return pd.DataFrame(novas)

# Usar no notebook:
vagas_realmente_novas = salvar_vagas_novas(df_vagas)
if not vagas_realmente_novas.empty:
    enviar_alerta_telegram(vagas_realmente_novas)
```

### 3.2 Descoberta via API Reversa (Técnica Avançada)

**O que é?** Inspecionar requisições do site para encontrar API oculta.

**Como fazer:**

1. **Abrir DevTools (F12)** em kpmg.inhire.app/vagas
2. **Ir em Network** → Refresh da página
3. **Filtrar por XHR/Fetch**
4. **Procurar por:**
   - Requisições GET/POST que retornam JSON
   - URLs contendo `api`, `jobs`, `vagas`, `positions`

**Exemplo hipotético:**
```python
# Se descobrir que existe uma API em:
# https://api.inhire.app/v1/companies/{empresa}/jobs

def extrair_vagas_api(empresa):
    """Método muito mais rápido e confiável que scraping HTML"""
    
    api_url = f"https://api.inhire.app/v1/companies/{empresa}/jobs"
    
    headers = {
        'Accept': 'application/json',
        'User-Agent': ua.random
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            vagas = []
            for job in data.get('jobs', []):
                vagas.append({
                    'empresa': empresa.upper(),
                    'titulo': job['title'],
                    'link': job['url'],
                    'data_publicacao': job['published_at'],
                    'localizacao': job.get('location', ''),
                    'descricao': job.get('description', '')
                })
            
            return vagas
    except:
        pass
    
    return []
```

**IMPORTANTE:** APIs podem exigir autenticação ou ter rate limits.

### 3.3 Google Dorking Avançado

**Queries mais eficientes:**

```python
GOOGLE_DORKS = [
    # Buscar vagas específicas
    'site:inhire.app/vagas "analista de dados" "remoto"',
    'site:inhire.app/vagas "data analyst" "remote"',
    'site:inhire.app/vagas intitle:"Business Analyst"',
    
    # Descobrir empresas
    'site:*.inhire.app/vagas',
    'site:inhire.app inurl:vagas',
    
    # Por tecnologia
    'site:inhire.app/vagas "Python" "SQL" "remoto"',
    'site:inhire.app/vagas "Power BI" OR "Tableau"',
    
    # Por nível
    'site:inhire.app/vagas "junior" "dados"',
    'site:inhire.app/vagas "senior" "analytics"'
]
```

### 3.4 Processamento de Linguagem Natural Avançado

**Melhorar filtros usando spaCy ou NLTK:**

```python
# Instalar: pip install spacy
# python -m spacy download pt_core_news_sm

import spacy

nlp = spacy.load('pt_core_news_sm')

def analise_nlp_vaga(texto):
    """Analisa semanticamente se vaga é relevante"""
    
    doc = nlp(texto.lower())
    
    # Extrai entidades
    tecnologias = ['python', 'sql', 'power bi', 'tableau', 'excel']
    areas = ['dados', 'analytics', 'business intelligence', 'bi']
    
    score = 0
    
    # Verifica presença de tecnologias
    for tech in tecnologias:
        if tech in texto.lower():
            score += 2
    
    # Verifica presença de áreas
    for area in areas:
        if area in texto.lower():
            score += 3
    
    # Analisa contexto
    if 'remoto' in texto.lower() and 'presencial' not in texto.lower():
        score += 5
    
    return score >= 5  # Threshold ajustável
```

---

## 🔧 PARTE 4: Troubleshooting Comum

### Problema 1: "Nenhuma vaga encontrada"

**Causa:** HTML do InHire mudou.

**Solução:**
1. Abra manualmente uma página (ex: kpmg.inhire.app/vagas)
2. Inspecione elementos (F12)
3. Identifique a estrutura HTML das vagas
4. Ajuste seletores no código:
   ```python
   # Exemplo de ajuste:
   vaga_elements = soup.find_all('div', class_='job-card')  # Classe específica
   ```

### Problema 2: "Bloqueado pelo servidor (403/429)"

**Causa:** Muitas requisições rápidas.

**Solução:**
1. Aumente `DELAY_REQUISICOES` para 5-10 segundos
2. Adicione User-Agent rotation (já implementado)
3. Use proxies (avançado):
   ```python
   proxies = {
       'http': 'http://proxy.com:8080',
       'https': 'http://proxy.com:8080'
   }
   response = requests.get(url, proxies=proxies)
   ```

### Problema 3: Telegram não envia

**Checklist:**
- [ ] Token está correto?
- [ ] Chat ID está correto?
- [ ] Você iniciou conversa com o bot?
- [ ] Biblioteca instalada? `pip install python-telegram-bot`
- [ ] Firewall bloqueando? Teste com VPN

---

## 📊 PARTE 5: Análise de Dados Avançada

### Dashboard com Streamlit

**Criar interface visual para análise:**

```python
# Arquivo: dashboard_vagas.py
import streamlit as st
import pandas as pd
import sqlite3

st.title('📊 Dashboard de Vagas InHire')

# Conectar ao banco
conn = sqlite3.connect('vagas_historico.db')
df = pd.read_sql('SELECT * FROM vagas', conn)

# Métricas
col1, col2, col3 = st.columns(3)
col1.metric("Total de Vagas", len(df))
col2.metric("Empresas", df['empresa'].nunique())
col3.metric("Vagas Hoje", len(df[df['data_descoberta'] == pd.Timestamp.today().date()]))

# Gráficos
st.subheader('Vagas por Empresa')
st.bar_chart(df['empresa'].value_counts())

st.subheader('Tendência no Tempo')
df['data_descoberta'] = pd.to_datetime(df['data_descoberta'])
timeline = df.groupby(df['data_descoberta'].dt.date).size()
st.line_chart(timeline)

# Tabela filtrada
st.subheader('Vagas Recentes')
st.dataframe(df.tail(20))
```

**Rodar:**
```bash
streamlit run dashboard_vagas.py
```

### Relatório Semanal Automatizado

```python
from datetime import datetime, timedelta

def gerar_relatorio_semanal():
    """Gera relatório consolidado da semana"""
    
    conn = sqlite3.connect('vagas_historico.db')
    
    # Últimos 7 dias
    data_inicio = datetime.now() - timedelta(days=7)
    
    df = pd.read_sql(f'''
        SELECT * FROM vagas 
        WHERE data_descoberta >= '{data_inicio.isoformat()}'
    ''', conn)
    
    # Estatísticas
    relatorio = f"""
    📊 RELATÓRIO SEMANAL - Monitor de Vagas InHire
    
    📅 Período: {data_inicio.strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')}
    
    📈 NÚMEROS:
    - Total de vagas: {len(df)}
    - Empresas ativas: {df['empresa'].nunique()}
    - Média diária: {len(df)/7:.1f} vagas
    
    🏆 TOP 5 EMPRESAS:
    {df['empresa'].value_counts().head().to_string()}
    
    🔥 VAGAS MAIS RECENTES:
    {df[['empresa', 'titulo']].tail(5).to_string(index=False)}
    """
    
    return relatorio

# Enviar por email ou Telegram
```

---

## 🎓 PARTE 6: Recursos de Aprendizado

### Livros Recomendados
- **"Web Scraping with Python"** - Ryan Mitchell
- **"Automate the Boring Stuff with Python"** - Al Sweigart

### Cursos Online
- [Real Python - Web Scraping](https://realpython.com/beautiful-soup-web-scraper-python/)
- [Scrapy Tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)

### Ferramentas Úteis
- **SelectorGadget:** Ferramenta Chrome para encontrar seletores CSS
- **Postman:** Testar APIs
- **Scrapy:** Framework profissional de web scraping

---

## ⚖️ PARTE 7: Considerações Legais e Éticas

### Boas Práticas
1. **Respeite robots.txt:**
   ```python
   from urllib.robotparser import RobotFileParser
   
   rp = RobotFileParser()
   rp.set_url("https://empresa.inhire.app/robots.txt")
   rp.read()
   
   if rp.can_fetch("*", "https://empresa.inhire.app/vagas"):
       # OK para scraping
   ```

2. **Rate Limiting:**
   - Não faça mais que 1 requisição por segundo
   - Use delays entre requisições
   - Implemente backoff exponencial em erros

3. **Identificação:**
   ```python
   headers = {
       'User-Agent': 'MonitorVagasBot/1.0 (contato@email.com)'
   }
   ```

4. **Respeite termos de uso** do InHire

### O que NÃO fazer
- ❌ Não venda dados coletados
- ❌ Não sobrecarregue servidores
- ❌ Não ignore rate limits
- ❌ Não use dados para spam

---

## 📞 Suporte

**Problemas comuns?** Verifique:
1. Versões das bibliotecas (`pip list`)
2. Logs de erro completos
3. Estrutura HTML atual do site

**Melhorias futuras:**
- Integração com LinkedIn
- Análise de salários
- Matching automático com seu perfil
- Alertas por email

---

**Desenvolvido com ❤️ por um Python Developer Sênior**  
**Versão:** 1.0  
**Última atualização:** Março 2026
