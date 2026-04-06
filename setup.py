from setuptools import setup, find_packages

setup(
    name="tcc-redacao-ia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "google-generativeai",
        "python-dotenv",
        "pandas",
        "numpy",
        "spacy",
        "langchain",
        "langchain-community",
        "faiss-cpu"
    ]
)