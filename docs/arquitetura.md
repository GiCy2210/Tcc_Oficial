# Arquitetura do Sistema

## Componentes

### 1. Camada de Apresentação (app/)
- Streamlit para interface web
- Páginas: corretor, análise de erros, plano de estudos

### 2. Camada de Serviços (src/services/)
- `gemini_service.py`: Comunicação com API
- `correction_service.py`: Lógica de correção
- `error_service.py`: Análise de erros
- `study_plan_service.py`: Geração de plano

### 3. Camada de Prompts (src/prompts/)
- Templates otimizados para cada funcionalidade

### 4. Camada de Utilitários (src/utils/)
- Validação, parsing, normalização

## Fluxo de Dados
1. Usuário envia redação via Streamlit
2. Backend valida entrada
3. Serviço de correção monta prompt e chama Gemini
4. Resposta JSON é parseada e validada
5. Interface exibe resultados
## Visão Geral