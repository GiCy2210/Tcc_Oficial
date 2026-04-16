# 📝 CorretorIA — Sistema Inteligente de Correção de Redações ENEM

> TCC — Curso de [Seu Curso] · [Sua Instituição] · [Ano]

Sistema de apoio pedagógico baseado em **Inteligência Artificial (Google Gemini)** para correção automática de redações no estilo ENEM, avaliando as **5 competências oficiais do INEP** com feedback detalhado e plano de estudos personalizado.

---

## 🎯 Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| ✅ Correção por competência | Notas de 0 a 200 para C1, C2, C3, C4 e C5 |
| ✅ Justificativa técnica | Explicação baseada nos critérios do INEP |
| ✅ Detecção de zeradores | Fuga ao tema e violação de direitos humanos |
| ✅ Plano de estudos | Sugestões práticas por área de melhoria |
| ✅ Histórico | Todas as correções salvas localmente |
| ✅ Estatísticas | Médias e evolução por competência |

---

## 🚀 Como Executar

### 1. Clone o repositório
```bash
git clone https://github.com/GiCy2210/Tcc_Oficial
cd Tcc_Oficial
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Obtenha sua chave da API Gemini
Acesse [aistudio.google.com/apikey](https://aistudio.google.com/apikey) e crie uma chave gratuita.

### 4. Execute o sistema
```bash
python run.py
```

### 5. Abra no navegador
Acesse: **http://localhost:5000**

---

## 🏗️ Arquitetura do Projeto

```
Tcc_Oficial/
├── app/
│   ├── index.html          # Interface HTML/CSS/JS
│   └── server.py           # API Flask (backend)
├── src/
│   ├── correction_service.py   # Lógica de correção com Gemini
│   └── database_service.py     # Persistência SQLite
├── data/
│   └── historico.db        # Banco de dados (gerado automaticamente)
├── tests/                  # Testes unitários
├── requirements.txt
└── run.py                  # Ponto de entrada
```

---

## 🧠 Tecnologias Utilizadas

- **Google Gemini 2.0 Flash** — Modelo de linguagem para correção
- **Flask** — Servidor web / API REST
- **SQLite** — Persistência de dados local
- **HTML5 / CSS3 / JavaScript** — Interface do usuário

---

## 📊 As 5 Competências do ENEM

| # | Competência | Peso |
|---|---|---|
| C1 | Domínio da norma padrão da língua escrita | 0–200 |
| C2 | Compreensão da proposta e aplicação de conceitos | 0–200 |
| C3 | Seleção, relação e organização de informações | 0–200 |
| C4 | Mecanismos linguísticos para construção da argumentação | 0–200 |
| C5 | Elaboração de proposta de intervenção (com respeito aos DH) | 0–200 |

---

## 👨‍🎓 Autor

**[Seu Nome]**  
[Seu Curso] — [Sua Instituição]  
Orientador: [Nome do Orientador]

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos (TCC).