# 🚀 Deploy do App no Streamlit Cloud

## 🎯 Por Que Streamlit Cloud?

### ✅ Vantagens ENORMES:

1. **IP Diferente a Cada Execução**
   - Streamlit roda em servidores na nuvem
   - Load balancing = IPs rotativos
   - **Google NÃO consegue bloquear!** 🎉

2. **100% GRÁTIS**
   - Streamlit Community Cloud = $0
   - Hospedagem ilimitada
   - Sem cartão de crédito

3. **Interface Visual Bonita**
   - ✅ Checkboxes para selecionar empresas
   - ✅ Sliders para configurações
   - ✅ Botão "Buscar Vagas"
   - ✅ Tabela de resultados
   - ✅ Download direto CSV/Excel

4. **Compartilhável**
   - Link público: `seu-usuario.streamlit.app`
   - Amigos podem usar também
   - Sem instalar nada

5. **Acesso de Qualquer Lugar**
   - Navegador web
   - Celular, tablet, PC
   - Não precisa Python instalado

---

## 📋 Passo a Passo COMPLETO

### Passo 1: Criar Conta no GitHub (se não tiver)

1. Acesse: https://github.com
2. Clique em "Sign Up"
3. Crie sua conta (grátis)

---

### Passo 2: Criar Repositório no GitHub

1. **Login** no GitHub
2. Clique no **"+"** (canto superior direito) → **New repository**
3. Configure:
   - **Repository name:** `monitor-vagas-inhire`
   - **Description:** Monitor de vagas remotas InHire
   - **Public** (deixe público)
   - ✅ **Add a README file** (marque)
4. Clique em **Create repository**

---

### Passo 3: Upload dos Arquivos

Você precisa fazer upload de 2 arquivos:

1. **`streamlit_app.py`** (código principal)
2. **`requirements.txt`** (dependências)

**Como fazer upload:**

**Opção A - Via Interface Web (Mais Fácil):**

1. No seu repositório, clique em **Add file** → **Upload files**
2. Arraste os 2 arquivos:
   - `streamlit_app.py`
   - `requirements.txt`
3. Escreva um commit message: "Adicionar app monitor de vagas"
4. Clique em **Commit changes**

**Opção B - Via Git (Se souber):**

```bash
git clone https://github.com/SEU-USUARIO/monitor-vagas-inhire.git
cd monitor-vagas-inhire
# Copie os arquivos para esta pasta
git add streamlit_app.py requirements.txt
git commit -m "Adicionar app monitor de vagas"
git push
```

---

### Passo 4: Criar Conta no Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em **Sign up** → **Continue with GitHub**
3. Autorize Streamlit a acessar seu GitHub
4. Confirm com sua conta GitHub

---

### Passo 5: Deploy do App

1. No Streamlit Cloud, clique em **New app**
2. Configure:
   - **Repository:** `seu-usuario/monitor-vagas-inhire`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** escolha um nome (ex: `monitor-vagas-inhire`)
3. Clique em **Deploy!**

**Aguarde ~2-3 minutos** enquanto o app é implantado.

---

### Passo 6: Usar o App! 🎉

Seu app estará disponível em:
```
https://SEU-USUARIO-monitor-vagas-inhire.streamlit.app
```

**Interface:**
- Sidebar esquerda: Configurações
- Botão central: "🚀 BUSCAR VAGAS"
- Resultados: Tabela + Download CSV/Excel

---

## 🎨 Como Usar o App

### 1. Configurar (Sidebar)

**Empresas:**
- Selecione empresas prioritárias
- ✅ Marque "Incluir busca geral" para todas

**Cargos:**
- Já vem configurado com:
  - analista de dados
  - data analyst
  - business analyst
  - etc.
- Adicione/remova conforme quiser

**Modalidade:**
- Já vem com: remoto, remote, home office

**Avançado:**
- Ajuste número de resultados
- Aumente delay se for bloqueado (improvável!)

### 2. Executar Busca

1. Clique em **🚀 BUSCAR VAGAS**
2. Aguarde ~20-40 segundos
3. Veja resultados em tempo real

### 3. Ver Resultados

- **Métricas:** Total, empresas, etc.
- **Gráfico:** Distribuição por empresa
- **Tabela:** Todas as vagas
- **Filtro:** Por empresa específica

### 4. Download

- **⬇️ Download CSV:** Para Excel/Análise
- **⬇️ Download Excel:** Formatado

---

## 🔧 Configurações Recomendadas

### Para Mais Vagas:
- Resultados da busca geral: **100**
- Resultados por empresa: **20**
- Marque **todas** as empresas relevantes

### Para Mais Velocidade:
- Resultados da busca geral: **30**
- Resultados por empresa: **10**
- Selecione **3-5 empresas** apenas

### Se For Bloqueado (improvável):
- Delay entre buscas: **5-10 segundos**
- Reduza número de resultados
- Aguarde 30 min e tente novamente

---

## 🎯 Vantagens vs Notebook Local

| Aspecto | Notebook Local | Streamlit Cloud |
|---------|----------------|-----------------|
| **Bloqueio Google** | ❌ Muito comum | ✅ Muito raro |
| **IP Tracking** | ❌ Sempre seu IP | ✅ IP rotativo |
| **Instalação** | ⚠️ Precisa Python | ✅ Só navegador |
| **Interface** | ⚠️ Código | ✅ Visual bonita |
| **Compartilhar** | ❌ Difícil | ✅ Link público |
| **Custo** | 💰 Grátis | 💰 Grátis |
| **Acesso** | 💻 Só seu PC | 🌐 Qualquer lugar |

---

## 🚀 Melhorias Futuras

Você pode adicionar ao app:

### 1. Banco de Dados (Histórico)
```python
# Salvar vagas em SQLite
# Detectar vagas novas vs antigas
# Mostrar "Novas hoje: 5"
```

### 2. Telegram (Alertas)
```python
# Configurar bot token via secrets
# Enviar notificações de novas vagas
```

### 3. Agendamento
```python
# Usar Streamlit secrets
# Agendar execução automática
# Email com resultados
```

### 4. Filtros Avançados
```python
# Filtro por salário
# Filtro por senioridade
# Palavras-chave customizadas
```

---

## 📱 Uso no Celular

**Sim, funciona perfeitamente!**

1. Abra o link no navegador do celular
2. Interface se adapta automaticamente
3. Configure e busque normalmente
4. Baixe CSV/Excel direto no celular

---

## 🔒 Segurança & Privacidade

### Seus dados estão seguros:

- ✅ Não salva nenhuma informação pessoal
- ✅ Buscas são anônimas (via Streamlit)
- ✅ Código é open-source (você vê tudo)
- ✅ Sem login ou senha necessária

### O que o app faz:

1. Busca no Google quando você clica no botão
2. Processa resultados
3. Exibe na tela
4. **Não salva nada** (cada execução é isolada)

---

## ❓ FAQ

### Q: Precisa pagar algo?
**A:** NÃO! Streamlit Community Cloud é 100% grátis.

### Q: Precisa cartão de crédito?
**A:** NÃO!

### Q: Quantas buscas posso fazer?
**A:** Ilimitadas! (mas seja gentil, não abuse)

### Q: Funciona no celular?
**A:** Sim! Perfeitamente.

### Q: Posso compartilhar com amigos?
**A:** Sim! Só enviar o link.

### Q: Quanto tempo fica no ar?
**A:** Para sempre (enquanto Streamlit existir)

### Q: E se Google bloquear?
**A:** Muito improvável (IP rotativo), mas aumente o delay se acontecer.

### Q: Posso editar o código depois?
**A:** Sim! Edite no GitHub, Streamlit atualiza automaticamente.

---

## 🎉 Pronto!

**Você agora tem:**
- ✅ App web profissional
- ✅ Hospedado gratuitamente
- ✅ Interface visual bonita
- ✅ Sem bloqueios do Google
- ✅ Acesso de qualquer lugar
- ✅ Compartilhável

**Link do app:**
```
https://SEU-USUARIO-monitor-vagas-inhire.streamlit.app
```

**Use, abuse e seja feliz! 🚀**

---

## 📞 Suporte

**Problemas no deploy?**
- Verifique se ambos arquivos estão no GitHub
- Confirme nomes: `streamlit_app.py` e `requirements.txt`
- Veja logs no Streamlit Cloud (botão "Manage app")

**App não funciona?**
- Verifique logs (botão "⋮" → "Logs")
- Bibliotecas instalaram? (veja requirements.txt)
- Tente fazer redeploy (Manage app → Reboot)

**Bloqueado?**
- Aumente delay para 5-10 segundos
- Reduza número de resultados
- Aguarde 30 min e tente novamente

---

**Desenvolvido com ❤️ para encontrar vagas incríveis! 🎯**
