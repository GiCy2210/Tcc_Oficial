# Guia de Deploy

## Opção 1 — Local (desenvolvimento)

```bash
python run.py
# Acesse: http://localhost:5000
```

---

## Opção 2 — Render.com (gratuito, recomendado para apresentação)

1. Crie conta em [render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Crie um **Web Service** com:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
4. Adicione variável de ambiente: `GEMINI_API_KEY=sua_chave`
5. Deploy automático a cada `git push`

---

## Opção 3 — Railway.app (alternativa gratuita)

1. Acesse [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Selecione `Tcc_Oficial`
4. Adicione variável: `GEMINI_API_KEY=sua_chave`
5. O Railway detecta automaticamente o `run.py`

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `GEMINI_API_KEY` | Opcional | Se definida, dispensa digitação na interface |

---

## Notas para Produção

- O SQLite funciona bem para apresentação do TCC
- Para produção real, migrar para PostgreSQL
- A chave da API pode ser inserida diretamente na interface (sem expor no código)