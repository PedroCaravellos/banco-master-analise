# Guia de Deploy — GitHub + Streamlit Cloud

## Passo 1 — Subir para o GitHub

```bash
# Dentro da pasta do projeto
cd banco_master

git init
git add .
git commit -m "feat: análise financeira Banco Master v1.0

- Dataset histórico 2020-2024 (10 períodos semestrais)
- Script de coleta via IF.data BCB (src/coleta_dados.py)
- Dashboard Streamlit com 5 seções interativas
- Regressão linear com projeção 2025
- Notebook de análise exploratória"

git branch -M main
git remote add origin https://github.com/SEU-USUARIO/banco-master-analise.git
git push -u origin main
```

## Passo 2 — Deploy no Streamlit Cloud (gratuito)

1. Acesse **share.streamlit.io** e faça login com GitHub
2. Clique em **"New app"**
3. Preencha:
   - **Repository:** `SEU-USUARIO/banco-master-analise`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Clique em **Deploy!**

O Streamlit Cloud instala as dependências do `requirements.txt` automaticamente.

## Passo 3 — URL pública

Após o deploy (aprox. 2 minutos), você receberá uma URL do tipo:
```
https://seu-usuario-banco-master-analise-app-XXXXX.streamlit.app
```

## Atualizar o deploy

Qualquer `git push` na branch `main` atualiza o app automaticamente.

```bash
# Após editar arquivos
git add .
git commit -m "fix: atualizar dados 2025"
git push
```

## Rodar localmente (desenvolvimento)

```bash
pip install -r requirements.txt
streamlit run app.py
# Abre em http://localhost:8501
```
