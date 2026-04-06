"""
Utilitários para Processamento de Linguagem Natural com spaCy
"""
import spacy
from typing import List, Dict, Tuple

class AnalisadorTexto:
    """Classe para análise de texto usando spaCy"""
    
    def __init__(self):
        """Inicializa o modelo do spaCy"""
        self.nlp = self._carregar_modelo()
    
    def _carregar_modelo(self):
        """Carrega o modelo de português"""
        try:
            # Tenta carregar modelo médio (recomendado)
            return spacy.load("pt_core_news_md")
        except OSError:
            try:
                # Fallback para modelo pequeno
                return spacy.load("pt_core_news_sm")
            except OSError:
                raise Exception(
                    "Modelo spaCy não encontrado! Execute:\n"
                    "python -m spacy download pt_core_news_md"
                )
    
    def analisar_gramatica(self, texto: str) -> Dict:
        """
        Analisa aspectos gramaticais do texto
        
        Returns:
            Dict com tokens, entidades, e análise gramatical
        """
        doc = self.nlp(texto)
        
        # Estatísticas básicas
        num_tokens = len(doc)
        num_sentencas = len(list(doc.sents))
        
        # Contagem por classe gramatical
        classes_gramaticais = {
            "substantivos": 0,
            "verbos": 0,
            "adjetivos": 0,
            "advérbios": 0,
            "conjunções": 0,
            "preposições": 0
        }
        
        for token in doc:
            if token.pos_ == "NOUN":
                classes_gramaticais["substantivos"] += 1
            elif token.pos_ == "VERB":
                classes_gramaticais["verbos"] += 1
            elif token.pos_ == "ADJ":
                classes_gramaticais["adjetivos"] += 1
            elif token.pos_ == "ADV":
                classes_gramaticais["advérbios"] += 1
            elif token.pos_ == "CONJ" or token.pos_ == "SCONJ":
                classes_gramaticais["conjunções"] += 1
            elif token.pos_ == "ADP":
                classes_gramaticais["preposições"] += 1
        
        # Extrai entidades nomeadas
        entidades = []
        for ent in doc.ents:
            entidades.append({
                "texto": ent.text,
                "tipo": ent.label_,
                "descricao": spacy.explain(ent.label_)
            })
        
        return {
            "num_tokens": num_tokens,
            "num_sentencas": num_sentencas,
            "classes_gramaticais": classes_gramaticais,
            "entidades": entidades,
            "doc": doc  # Retorna o documento processado
        }
    
    def extrair_palavras_chave(self, texto: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extrai palavras-chave baseado em frequência e importância
        
        Args:
            texto: Texto para análise
            top_n: Número de palavras-chave a retornar
        
        Returns:
            Lista de tuplas (palavra, relevância)
        """
        doc = self.nlp(texto)
        
        # Filtra palavras significativas (substantivos, verbos, adjetivos)
        palavras_significativas = {}
        
        for token in doc:
            if token.pos_ in ["NOUN", "VERB", "ADJ"] and not token.is_stop:
                palavra = token.lemma_.lower()
                if len(palavra) > 3:  # Ignora palavras muito curtas
                    palavras_significativas[palavra] = palavras_significativas.get(palavra, 0) + 1
        
        # Ordena por frequência
        palavras_ordenadas = sorted(
            palavras_significativas.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return palavras_ordenadas[:top_n]
    
    def detectar_repeticao(self, texto: str, limite: int = 3) -> List[Dict]:
        """
        Detecta palavras repetidas no texto
        
        Args:
            texto: Texto para análise
            limite: Número máximo de repetições aceitável
        
        Returns:
            Lista de palavras repetidas com contagem
        """
        doc = self.nlp(texto)
        
        # Conta frequência de cada palavra (lematizada)
        frequencia = {}
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 3:
                palavra = token.lemma_.lower()
                frequencia[palavra] = frequencia.get(palavra, 0) + 1
        
        # Filtra palavras repetidas acima do limite
        repeticoes = []
        for palavra, count in frequencia.items():
            if count > limite:
                repeticoes.append({
                    "palavra": palavra,
                    "vezes": count,
                    "sugestao": f"Evite repetir '{palavra}'. Use sinônimos."
                })
        
        return repeticoes
    
    def calcular_densidade_lexical(self, texto: str) -> float:
        """
        Calcula densidade lexical (proporção de palavras de conteúdo)
        
        Returns:
            Float entre 0 e 1 (maior = mais rico lexicalmente)
        """
        doc = self.nlp(texto)
        
        palavras_conteudo = 0
        total_palavras = 0
        
        for token in doc:
            if not token.is_punct:
                total_palavras += 1
                if token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"]:
                    palavras_conteudo += 1
        
        if total_palavras == 0:
            return 0
        
        return palavras_conteudo / total_palavras

# Instância global para uso em todo o projeto
analisador = AnalisadorTexto()