"""
Módulo de Validação — compara notas da IA com notas humanas.
Essencial para o capítulo de Resultados do TCC.
"""
import json
import csv
from pathlib import Path
from correction_service import corrigir_redacao, resultado_para_dict

REDACOES_VALIDACAO = [
    {
        "id": 1,
        "tema": "Manipulação do comportamento do usuário pelo controle de dados",
        "nota_humano": 1000,
        "nivel": "excelente",
        "redacao": """
A era digital trouxe consigo uma nova forma de poder: o controle dos dados pessoais.
Empresas de tecnologia coletam informações sobre hábitos, preferências e comportamentos
dos usuários para direcionar conteúdos e influenciar decisões de consumo e, até mesmo,
políticas. Esse fenômeno, denominado capitalismo de vigilância pela socióloga Shoshana
Zuboff, representa uma ameaça à autonomia individual e à democracia.

No contexto brasileiro, esse problema se agrava pela ausência de letramento digital
adequado. Segundo dados do IBGE, mais de 80% dos brasileiros acessam a internet
exclusivamente pelo celular, tornando-se alvos fáceis de algoritmos que exploram
vulnerabilidades cognitivas. O filósofo Byung-Chul Han alerta que a sociedade do
desempenho cria indivíduos que se autoexploram, entregando voluntariamente seus dados
em troca de entretenimento imediato.

A manipulação do comportamento vai além do consumo: afeta eleições, como demonstrado
pelo escândalo da Cambridge Analytica, e alimenta câmaras de eco que radicalizam
opiniões. A polarização política observada no Brasil nas últimas décadas tem relação
direta com algoritmos que priorizam conteúdos emocionalmente carregados para maximizar
o engajamento, independentemente de sua veracidade.

Portanto, é fundamental que o Estado brasileiro, por meio do Congresso Nacional, aprimore
a Lei Geral de Proteção de Dados (LGPD), estabelecendo punições mais rígidas para o
uso indevido de dados e exigindo transparência algorítmica das plataformas digitais.
Além disso, o Ministério da Educação deve incluir o letramento digital crítico na Base
Nacional Comum Curricular, formando cidadãos capazes de compreender e questionar os
mecanismos de manipulação a que estão submetidos — condição indispensável para o
exercício pleno da cidadania na sociedade contemporânea.
        """.strip()
    },
    {
        "id": 2,
        "tema": "Desafios para a valorização de comunidades e povos tradicionais no Brasil",
        "nota_humano": 680,
        "nivel": "mediano",
        "redacao": """
Os povos tradicionais do Brasil enfrentam muitos desafios atualmente. Indígenas,
quilombolas e ribeirinhos são grupos que vivem de forma diferente da sociedade urbana
e precisam de reconhecimento e respeito.

Um dos principais problemas é a questão das terras. Muitas comunidades tradicionais
não têm suas terras demarcadas, o que gera conflitos com fazendeiros e empresas que
querem explorar esses territórios. Sem terra, esses povos perdem sua identidade cultural
e seus meios de subsistência.

Outro desafio é a falta de acesso a serviços básicos como saúde e educação. As escolas
nas aldeias muitas vezes não têm professores qualificados e os postos de saúde são
insuficientes para atender toda a população. Isso prejudica o desenvolvimento dessas
comunidades.

Para resolver esses problemas, o governo deve investir mais em políticas públicas
específicas para os povos tradicionais, garantindo a demarcação das terras, o acesso
à saúde diferenciada e a educação intercultural. A sociedade civil também deve apoiar
essas comunidades, valorizando sua cultura e conhecimentos tradicionais.
        """.strip()
    },
    {
        "id": 3,
        "tema": "O estigma associado às doenças mentais na sociedade brasileira",
        "nota_humano": 320,
        "nivel": "fraco",
        "redacao": """
A saúde mental é muito importante nos dias de hoje. Muitas pessoas sofrem de depressão
ansiedade e outras doenças mentais mas tem vergonha de falar sobre isso por causa do
preconceito que existe na sociedade.

As pessoas que tem doenças mentais são muito discriminadas. Os amigos e familiares
muitas vezes não entendem e acham que é frescura ou fraqueza. Isso faz com que as
pessoas não procurem ajuda e fiquem cada vez piores.

Na escola e no trabalho também tem muito preconceito. As pessoas com problemas mentais
são vistas como incapazes ou perigosas, o que não é verdade. Isso prejudica muito a
vida dessas pessoas.

Eu acho que a solução é conscientizar as pessoas sobre as doenças mentais através de
campanhas nas redes sociais e na televisão. Assim as pessoas vão entender melhor e
parar de ter preconceito com quem sofre desses problemas.
        """.strip()
    },
]

def validar_sistema(api_key: str, salvar_csv: bool = True) -> list[dict]:
    resultados = []
    for caso in REDACOES_VALIDACAO:
        print(f"Validando redação {caso['id']} ({caso['nivel']})...")
        try:
            resultado_obj = corrigir_redacao(caso["redacao"], caso["tema"], api_key)
            resultado = resultado_para_dict(resultado_obj)
            nota_ia = resultado["nota_total"]
            nota_humano = caso["nota_humano"]
            diferenca = nota_ia - nota_humano
            comp = resultado["competencias"]
            entry = {
                "id": caso["id"],
                "tema": caso["tema"][:50] + "...",
                "nivel": caso["nivel"],
                "nota_humano": nota_humano,
                "nota_ia": nota_ia,
                "diferenca": diferenca,
                "diferenca_abs": abs(diferenca),
                "c1_ia": comp["c1"]["nota"],
                "c2_ia": comp["c2"]["nota"],
                "c3_ia": comp["c3"]["nota"],
                "c4_ia": comp["c4"]["nota"],
                "c5_ia": comp["c5"]["nota"],
            }
            resultados.append(entry)
            print(f"  Humano: {nota_humano} | IA: {nota_ia} | Diff: {diferenca:+d}")
        except Exception as e:
            print(f"  ERRO: {e}")

    if salvar_csv and resultados:
        Path("data").mkdir(exist_ok=True)
        with open("data/validacao.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        print("\n✅ Resultados salvos em data/validacao.csv")

    # Resumo
    if resultados:
        media_diff = sum(r["diferenca_abs"] for r in resultados) / len(resultados)
        print(f"\n📊 Diferença média absoluta: {media_diff:.1f} pontos")
        print(f"   (Em 1000 pontos = {media_diff/10:.1f}% de erro médio)")

    return resultados

if __name__ == "__main__":
    import os
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        key = input("Gemini API Key: ").strip()
    validar_sistema(key)