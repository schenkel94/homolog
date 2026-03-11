# 🔍 Monitor de Vagas InHire

> App web para encontrar vagas remotas de Analista de Dados na plataforma InHire

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-app.streamlit.app)

## 🎯 Sobre

Monitor automatizado que busca vagas de **Analista de Dados**, **Data Analyst**, **Business Analyst** e áreas relacionadas em empresas que usam a plataforma InHire.

### ✨ Funcionalidades

- 🔍 **Busca Automatizada** via Google Search
- 🏢 **60+ Empresas** cadastradas (Nubank, iFood, Stone, etc.)
- 🏠 **Filtro de Vagas Remotas**
- 📊 **Interface Visual** com Streamlit
- 💾 **Download CSV/Excel** dos resultados
- 📈 **Gráficos** de distribuição por empresa
- 🎨 **Filtros Interativos** por empresa

## 🚀 Demo Online

**Acesse o app:** Após fazer deploy, seu link será algo como `https://seu-usuario-monitor-vagas-inhire.streamlit.app`

Não precisa instalar nada! Funciona direto no navegador.

## 💡 Por Que Este Projeto?

### Problema:
- InHire é um SPA (Single Page Application)
- Carrega vagas via JavaScript
- Scraping tradicional não funciona
- Precisa visitar site por site manualmente

### Solução:
- ✅ Usa Google Search (já indexou as páginas)
- ✅ Filtra automaticamente por cargo + remoto
- ✅ Interface visual bonita
- ✅ Roda na nuvem (sem bloqueios de IP)

## 📋 Como Usar

### Opção 1: App Online (Recomendado)

1. Acesse o link do app
2. Configure empresas e keywords na sidebar
3. Clique em "🚀 BUSCAR VAGAS"
4. Veja resultados e baixe CSV/Excel

### Opção 2: Rodar Localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/monitor-vagas-inhire.git
cd monitor-vagas-inhire

# Instale dependências
pip install -r requirements.txt

# Execute o app
streamlit run streamlit_app.py
```

Acesse: `http://localhost:8501`

## 🏢 Empresas Monitoradas (60+)

Sympla • KPMG • Alura • iFood • Nubank • Stone • Creditas • Magalu • Deloitte • DB1 • e mais 50+

## 🔧 Configurações Personalizáveis

- Selecione empresas específicas ou busque em todas
- Customize keywords de cargos
- Ajuste modalidade (remoto, híbrido, etc.)
- Configure número de resultados
- Ajuste delays entre buscas

## 🛠️ Tecnologias

- **Python 3.9+**
- **Streamlit** - Interface web
- **googlesearch-python** - Busca no Google
- **Pandas** - Manipulação de dados
- **OpenPyXL** - Exportação Excel

## 📁 Estrutura do Projeto

```
monitor-vagas-inhire/
│
├── streamlit_app.py      # App principal
├── requirements.txt      # Dependências
└── README.md            # Este arquivo
```

## 🚀 Deploy no Streamlit Cloud (GRÁTIS!)

### Passo a Passo Rápido:

1. **Fork/Clone este repositório**
2. **Acesse:** https://streamlit.io/cloud
3. **Sign up** com GitHub
4. **New app** → Selecione seu repositório
5. **Deploy!**

Veja instruções detalhadas em `DEPLOY_STREAMLIT.md`

## ⚡ Vantagens do Deploy na Nuvem

| Vantagem | Descrição |
|----------|-----------|
| 🔒 **Sem Bloqueios** | IP rotativo do Streamlit |
| 💰 **Grátis** | Streamlit Community Cloud |
| 🌐 **Acesso Global** | De qualquer dispositivo |
| 📱 **Mobile-Friendly** | Funciona no celular |
| 🔗 **Compartilhável** | Link público para amigos |

## 📊 Exemplo de Uso

```python
# Configuração típica:
- Empresas selecionadas: Sympla, KPMG, iFood, Nubank, Stone
- Cargos: analista de dados, data analyst, business analyst
- Modalidade: remoto
- Resultados: 50 (geral) + 10 por empresa

# Resultado esperado:
- Tempo de execução: ~30 segundos
- Vagas encontradas: 20-50
- Download: CSV + Excel
```

## ⚠️ Notas Importantes

- **Rate Limiting:** Use delays adequados (2-5 segundos)
- **Vagas Novas:** Podem levar 24h para serem indexadas pelo Google
- **Bloqueios:** Muito raros no Streamlit Cloud (IP rotativo)

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push e abra um Pull Request

## 📝 To-Do / Roadmap

- [ ] Banco de dados para histórico de vagas
- [ ] Detecção de vagas novas (delta)
- [ ] Integração com Telegram para alertas
- [ ] Filtro por senioridade (júnior, pleno, sênior)
- [ ] Análise de tendências de mercado
- [ ] Dashboard analytics com gráficos avançados
- [ ] API REST para integração

## 📄 Licença

MIT License

## 📞 Suporte

- **Issues:** Use GitHub Issues para reportar bugs
- **Dúvidas:** GitHub Discussions

---

## ⭐ Gostou?

Se este projeto te ajudou, dê uma ⭐ no repositório!

**Desenvolvido com ❤️ para ajudar pessoas a encontrarem vagas incríveis!**

**Boa sorte na busca! 🚀**
