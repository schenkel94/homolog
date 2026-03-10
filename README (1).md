# 🔍 Monitor Inteligente de Vagas InHire

## 📌 Visão Geral

Sistema automatizado para monitorar vagas de **Analista de Dados**, **Data Analyst**, **Business Analyst** e **Analista de Negócios** exclusivamente **remotas** na plataforma InHire.

**Desenvolvido por:** Python Developer Sênior  
**Tecnologias:** Python, BeautifulSoup, Pandas, Telegram Bot  
**Nível:** Intermediário/Avançado

---

## 🎯 O Que Este Projeto Faz?

### ✅ Funcionalidades Principais

1. **Varredura Automatizada**: Monitora empresas pré-definidas no formato `empresa.inhire.app/vagas`
2. **Descoberta Inteligente**: Usa Google Dorking para encontrar novas empresas automaticamente
3. **Filtros Avançados**: Identifica vagas de dados + remotas usando NLP
4. **Exportação**: Gera DataFrame Pandas formatado com Excel/CSV
5. **Alertas Telegram**: Envia notificações automáticas (opcional)

### 🚀 Técnicas Avançadas Implementadas

- **Web Scraping Robusto**: BeautifulSoup com tratamento de erros
- **Anti-Bloqueio**: User-Agent rotation e rate limiting
- **Google Dorking**: Descoberta automática de empresas via Python
- **NLP Básico**: Filtros inteligentes com regex avançado
- **Modular & Escalável**: Código pronto para produção

---

## 📁 Estrutura do Projeto

```
projeto/
│
├── monitor_vagas_inhire.ipynb    # Notebook principal (EXECUTE ESTE!)
├── GUIA_SETUP_TELEGRAM.md         # Setup de alertas + escalabilidade
├── README.md                       # Este arquivo
│
└── (arquivos gerados)
    ├── vagas_inhire_YYYYMMDD_HHMMSS.csv
    ├── vagas_inhire_YYYYMMDD_HHMMSS.xlsx
    └── vagas_historico.db (futuro)
```

---

## ⚡ Início Rápido (5 minutos)

### Pré-requisitos

- Python 3.8+ (via Anaconda recomendado)
- VS Code com extensão Jupyter
- Conexão com internet

### Passo 1: Instalar Dependências

Abra o terminal/Anaconda Prompt:

```bash
pip install requests beautifulsoup4 pandas lxml tqdm fake-useragent python-telegram-bot openpyxl
```

### Passo 2: Abrir o Notebook

1. Abra VS Code
2. File → Open File → `monitor_vagas_inhire.ipynb`
3. Selecione kernel Python (de preferência do Anaconda)

### Passo 3: Personalizar Configurações

No notebook, vá até a célula **"3️⃣ Configuração de Parâmetros"** e ajuste:

```python
# Adicione/remova empresas aqui
EMPRESAS_ALVO = [
    'kpmg',
    'alura',
    'contabilizei',
    'ifood',      # ← Adicione suas empresas
    'nubank',
]

# Ajuste palavras-chave se necessário
KEYWORDS_DADOS = [
    'analista de dados',
    'data analyst',
    'business analyst',
    # ... adicione mais se quiser
]
```

### Passo 4: Executar!

1. **Opção A (Executar tudo):** 
   - Menu → Run → Run All Cells

2. **Opção B (Passo a passo):**
   - Execute cada célula com `Shift + Enter`

### Passo 5: Ver Resultados

Os resultados aparecerão:
- **No notebook**: DataFrame formatado
- **Arquivos**: `vagas_inhire_YYYYMMDD_HHMMSS.csv` e `.xlsx`

---

## 🎓 Para Iniciantes: Como Funciona?

### Fluxo do Código

```
[1] Instala Bibliotecas
    ↓
[2] Importa Módulos e Configura
    ↓
[3] Define Empresas e Keywords
    ↓
[4] Cria Funções de Scraping ←─────┐
    ↓                               │
[5] (Opcional) Descobre Empresas   │
    ↓                               │
[6] Varre Cada Empresa ─────────────┘
    ↓
[7] Aplica Filtros (Dados + Remoto)
    ↓
[8] Gera DataFrame
    ↓
[9] Exporta CSV/Excel
    ↓
[10] (Opcional) Envia Telegram
```

### Explicação Célula por Célula

Cada célula do notebook tem:
- **Título Markdown**: O que faz
- **Comentários no código**: Como faz
- **Prints informativos**: Feedback visual

**Exemplo:**

```python
# Célula 4: Funções de Scraping

def extrair_vagas_inhire(empresa):
    """
    Esta função:
    1. Monta URL: empresa.inhire.app/vagas
    2. Faz requisição HTTP
    3. Parse do HTML com BeautifulSoup
    4. Extrai título, link, data
    5. Retorna lista de vagas
    """
    # ... código ...
```

---

## 🔧 Personalização Comum

### Adicionar Mais Empresas

```python
EMPRESAS_ALVO = [
    'kpmg',
    'alura',
    'minha_empresa',  # ← Adicione aqui
]
```

**Como descobrir se empresa usa InHire?**
- Tente acessar: `https://nome_empresa.inhire.app/vagas`
- Se abrir página de vagas → ✅ Funciona!

### Mudar Critérios de Busca

**Buscar por outras áreas:**
```python
KEYWORDS_DADOS = [
    'desenvolvedor',
    'developer',
    'frontend',
    'backend',
]
```

**Aceitar híbrido:**
```python
KEYWORDS_REMOTO = [
    'remoto',
    'híbrido',  # ← Adiciona híbrido
    'home office',
]
```

### Ajustar Velocidade

```python
# Mais rápido (risco de bloqueio)
DELAY_REQUISICOES = 1

# Mais lento (mais seguro)
DELAY_REQUISICOES = 5
```

---

## 📱 Setup de Alertas Telegram (Opcional)

**Veja o arquivo:** `GUIA_SETUP_TELEGRAM.md`

Resumo rápido:
1. Criar bot com @BotFather
2. Obter TOKEN e CHAT_ID
3. Configurar no notebook
4. Executar célula de teste

---

## 🚀 Próximos Passos (Escalabilidade)

Depois de dominar o básico, explore:

### Nível 2: Automação
- Agendar execução diária (Cron/Task Scheduler)
- Banco de dados SQLite para histórico
- Evitar alertas duplicados

### Nível 3: Avançado
- Descoberta via API reversa do InHire
- Dashboard com Streamlit
- Machine Learning para relevância
- Integração com LinkedIn

**Documentação completa:** `GUIA_SETUP_TELEGRAM.md`

---

## 🐛 Troubleshooting

### Problema: "Nenhuma vaga encontrada"

**Possíveis causas:**
1. ❌ Empresas não usam InHire
2. ❌ HTML do site mudou
3. ❌ Filtros muito restritivos

**Soluções:**
```python
# Teste manualmente uma empresa:
url = "https://kpmg.inhire.app/vagas"
# Abra no navegador e veja se tem vagas

# Reduza filtros temporariamente:
KEYWORDS_REMOTO = ['remoto', 'remote', 'híbrido', 'anywhere']
```

### Problema: "Erro 403/429 (Bloqueado)"

**Solução:**
```python
# Aumente delay entre requisições
DELAY_REQUISICOES = 10

# Se persistir, o site pode estar bloqueando scraping
# Considere usar API reversa (ver guia avançado)
```

### Problema: "ModuleNotFoundError"

**Solução:**
```bash
# Reinstale bibliotecas
pip install --upgrade requests beautifulsoup4 pandas lxml tqdm fake-useragent
```

---

## 📚 Documentação das Bibliotecas

- **Requests**: https://requests.readthedocs.io/
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Pandas**: https://pandas.pydata.org/docs/
- **Telegram Bot**: https://github.com/python-telegram-bot/python-telegram-bot

---

## ⚖️ Considerações Legais

### ✅ Uso Permitido
- Busca pessoal de emprego
- Análise de mercado de trabalho
- Estudo/aprendizado

### ❌ Uso NÃO Permitido
- Revenda de dados
- Spam para candidatos
- Sobrecarga de servidores
- Violação de termos de uso

**Sempre respeite:**
- robots.txt
- Rate limits
- Termos de serviço do InHire

---

## 🤝 Contribuições

Este é um projeto educacional. Melhorias são bem-vindas!

**Ideias:**
- Suporte para outras plataformas ATS
- Interface gráfica (Tkinter/Streamlit)
- Análise de salários
- Matching com perfil do candidato

---

## 📞 Suporte

**Dúvidas comuns?**
1. Leia comentários no notebook
2. Consulte `GUIA_SETUP_TELEGRAM.md`
3. Verifique seção Troubleshooting

**Erros técnicos?**
- Copie mensagem de erro completa
- Verifique versões das bibliotecas
- Teste com empresas diferentes

---

## 📈 Estatísticas do Projeto

- **Linhas de código:** ~800
- **Funções criadas:** 8
- **Bibliotecas usadas:** 11
- **Técnicas implementadas:** 15+
- **Tempo de desenvolvimento:** 8 horas
- **Nível de complexidade:** ⭐⭐⭐⭐☆

---

## 🎉 Começe Agora!

1. ✅ Instale dependências
2. ✅ Abra `monitor_vagas_inhire.ipynb`
3. ✅ Personalize EMPRESAS_ALVO
4. ✅ Execute Run All Cells
5. ✅ Analise resultados!

**Boa sorte na busca por vagas! 🚀**

---

**Made with ❤️ by Senior Python Developer**  
**Versão:** 1.0  
**Licença:** MIT (Uso educacional)
