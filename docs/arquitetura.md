# Documentação Técnica — CorretorIA ENEM

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│                   USUÁRIO (Browser)                  │
│              app/index.html (HTML/CSS/JS)            │
└────────────────────────┬────────────────────────────┘
                         │ HTTP (fetch API)
                         ▼
┌─────────────────────────────────────────────────────┐
│              SERVIDOR (Flask — Python)               │
│                  app/server.py                       │
│                                                     │
│  POST /api/corrigir  →  correction_service.py       │
│  GET  /api/historico →  database_service.py         │
│  GET  /api/stats     →  database_service.py         │
└────────────────────────┬────────────────────────────┘
                         │
           ┌─────────────┴──────────────┐
           ▼                            ▼
┌──────────────────┐        ┌──────────────────────┐
│  Google Gemini   │        │  SQLite (local)       │
│  (API externa)   │        │  data/historico.db    │
└──────────────────┘        └──────────────────────┘
```

---

## Fluxo de Correção

1. Usuário cola a redação e clica em **Corrigir**
2. O frontend envia `POST /api/corrigir` com `{redacao, tema, api_key}`
3. O servidor valida os dados (tamanho, campos obrigatórios)
4. `correction_service.py` monta o prompt com os critérios do INEP
5. O Gemini 2.0 Flash processa e retorna JSON estruturado
6. O resultado é salvo no SQLite via `database_service.py`
7. O frontend renderiza notas, justificativas e plano de estudos

---

## Prompt Engineering

O sistema usa dois níveis de prompt:

### System Prompt
Define o papel do modelo como "corretor oficial do ENEM" e especifica:
- Escala de notas (0, 40, 80, 120, 160, 200) por competência
- Critérios de zeramento (fuga ao tema, violação de DH)
- Exigência de resposta em JSON puro

### User Prompt
Injeta o tema e o texto da redação, e especifica o schema JSON exato esperado na resposta.

Essa separação garante que o modelo mantenha o papel de corretor independentemente do conteúdo da redação.

---

## Schema JSON de Resposta

```json
{
  "fuga_ao_tema": false,
  "violacao_direitos_humanos": false,
  "competencias": {
    "c1": {
      "nota": 120,
      "justificativa": "string",
      "erros": ["string"],
      "dicas": ["string"]
    },
    "c2": { ... },
    "c3": { ... },
    "c4": { ... },
    "c5": { ... }
  },
  "nota_total": 600,
  "feedback_geral": "string",
  "plano_estudos": [
    {
      "competencia": "C1",
      "foco": "string",
      "exercicio": "string",
      "prioridade": "alta | media | baixa"
    }
  ]
}
```

---

## Banco de Dados (SQLite)

### Tabela: `correcoes`

| Coluna | Tipo | Descrição |
|---|---|---|
| id | INTEGER PK | Identificador único |
| data | TEXT | Timestamp ISO 8601 |
| tema | TEXT | Tema informado |
| redacao | TEXT | Primeiros 500 chars |
| nota_total | INTEGER | Nota final (0-1000) |
| c1..c5 | INTEGER | Nota por competência |
| fuga_ao_tema | INTEGER | 0 ou 1 |
| resultado_json | TEXT | JSON completo da resposta |

---

## Modelo de IA

| Parâmetro | Valor |
|---|---|
| Modelo | gemini-2.0-flash |
| Temperatura | padrão (controlada pelo prompt) |
| Max tokens | 2048 |
| Output | JSON estruturado |

O modelo `gemini-2.0-flash` foi escolhido por:
- Custo zero na camada gratuita do Google AI Studio
- Velocidade superior ao Gemini Pro para tarefas estruturadas
- Suporte a `system_instruction` para controle do papel do modelo

---

## Validação do Sistema

Para o capítulo de resultados do TCC, execute:

```bash
python src/validation_service.py
```

Isso irá:
1. Rodar 3 redações de níveis distintos (excelente, mediano, fraco)
2. Comparar nota da IA com nota humana esperada
3. Salvar tabela em `data/validacao.csv`
4. Exibir diferença média absoluta

---

## Como Rodar os Testes

```bash
pip install pytest
pytest tests/ -v
```

Cobertura atual: database_service, correction_service (lógica), rotas Flask.