# Requisitos do Sistema

## Funcionais
- [RF01] O sistema deve receber texto de redação via interface web
- [RF02] O sistema deve validar tamanho mínimo/máximo da redação
- [RF03] O sistema deve chamar API Gemini para correção
- [RF04] O sistema deve retornar notas por competência (0-200)
- [RF05] O sistema deve fornecer feedback textual
- [RF06] O sistema deve identificar erros gramaticais e argumentativos
- [RF07] O sistema deve gerar plano de estudos baseado nos erros

## Não-Funcionais
- [RNF01] Resposta da IA em menos de 15 segundos
- [RNF02] Interface responsiva (desktop/mobile)
- [RNF03] Código modular e documentado
- [RNF04] Configuração via variáveis de ambiente