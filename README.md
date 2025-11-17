# Document AI OCR with Gemini Extractor

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?style=for-the-badge&logo=fastapi)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud)

Este projeto implementa um pipeline robusto para extrair texto de documentos (como notas fiscais, faturas e recibos) usando a alta precisão do **Google Document AI** e, em seguida, utiliza o poder do **Google Gemini** para extrair e estruturar esses dados em um formato JSON limpo e previsível.

## Visão Geral

O objetivo principal é automatizar o processo de leitura e interpretação de documentos. O fluxo de trabalho é dividido em duas etapas principais:

1.  **OCR (Reconhecimento Óptico de Caracteres):** O Google Document AI é usado para processar arquivos PDF ou imagens e extrair todo o texto bruto contido neles.
2.  **Extração de Dados Estruturados:** O texto bruto extraído é então enviado ao Google Gemini, que, com base em um prompt de engenharia, identifica, extrai e formata as informações relevantes (como CNPJ do emissor, valor total, data de emissão, etc.) em um objeto JSON.

## Arquitetura

O projeto oferece duas maneiras de interagir com o pipeline:

```mermaid
graph TD
    subgraph "Entrada"
        A[Arquivo Local .pdf/.jpg]
        B[URI de Arquivo no GCS]
    end

    subgraph "Processamento"
        C[Script Local (main.py)]
        D[API REST (api.py)]
    end

    subgraph "Serviços Externos"
        E[Google Document AI OCR]
        F[Google Gemini API]
    end

    subgraph "Saída"
        G[Arquivos .txt e .json no diretório /output]
        H[Resposta JSON da API]
    end

    A --> C
    B --> D
    C --> E --> F --> G
    D --> E --> F --> H
```

## Funcionalidades

- **OCR de Alta Precisão:** Utiliza o processador de OCR do Google Document AI, otimizado para documentos.
- **Extração Inteligente com LLM:** Usa o Gemini para interpretar o contexto do texto e extrair dados de forma flexível, sem a necessidade de templates rígidos.
- **Suporte a Múltiplas Fontes:** Processa tanto arquivos locais quanto documentos armazenados no Google Cloud Storage.
- **Interface Dupla:**
  - **Script de Linha de Comando:** Ideal para processamento em lote e testes locais (`main.py`).
  - **API RESTful:** Endpoint FastAPI (`/analyze-document`) para fácil integração com outros sistemas e aplicações web.
- **Configuração Simplificada:** Gerenciamento de chaves e IDs através de variáveis de ambiente com um arquivo `.env`.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes pré-requisitos:

1.  **Python 3.9+**
2.  **Conta no Google Cloud:**
    - Um projeto no GCP criado.
    - A **API do Document AI** habilitada.
    - Um **Processador de OCR** criado no Document AI.
    - Uma **Conta de Serviço** com permissões para o Document AI (`roles/documentai.apiUser`) e, se usar a API, para o Cloud Storage (`roles/storage.objectViewer`).
    - O arquivo de credenciais JSON da conta de serviço.
3.  **Chave de API do Google Gemini:**
    - Uma chave de API gerada no Google AI Studio.

## Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/gemini-document-ai-ocr.git
    cd gemini-document-ai-ocr
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    (Crie um arquivo `requirements.txt` com as bibliotecas necessárias e execute o comando abaixo)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as credenciais do Google Cloud:**
    Defina a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS` para apontar para o seu arquivo JSON da conta de serviço.
    ```bash
    # Windows (PowerShell)
    $env:GOOGLE_APPLICATION_CREDENTIALS="C:\caminho\para\sua-chave.json"
    # macOS/Linux
    export GOOGLE_APPLICATION_CREDENTIALS="/caminho/para/sua-chave.json"
    ```

5.  **Configure as variáveis de ambiente do projeto:**
    Renomeie o arquivo `.env.example` para `.env` e preencha com suas informações.

    ```ini
    # .env

    # Google Cloud Project ID
    PROJECT_ID="seu-gcp-project-id"

    # Localização do seu processador do Document AI (ex: "us" ou "eu")
    LOCATION="us"

    # ID do seu processador de OCR do Document AI
    OCR_PROCESSOR_ID="seu-ocr-processor-id"

    # Sua chave de API do Google Gemini
    GEMINI_API_KEY="sua-gemini-api-key"
    ```

## Como Usar

### 1. Processando um Arquivo Local (Script)

Para processar um documento que está na sua máquina local, edite o arquivo `main.py` para apontar para o seu arquivo e execute-o.

```python
// main.py
if __name__ == '__main__':
    # Altere este caminho para o seu arquivo
    pdf_to_process = r'examples/NF_SIMPLES.pdf'
    run(pdf_to_process)
```

Execute o script:
```bash
python main.py
```
Os resultados (texto bruto e JSON estruturado) serão salvos no diretório `output/`.

### 2. Usando a API REST

A API permite processar documentos que estão em um bucket do Google Cloud Storage.

**Inicie o servidor:**
```bash
uvicorn api:app --reload
```
O servidor estará disponível em `http://127.0.0.1:8000`.

**Acesse a documentação interativa:**
Abra seu navegador e acesse http://127.0.0.1:8000/docs para ver a documentação do Swagger UI e testar o endpoint.

**Exemplo de requisição com `curl`:**

Envie uma requisição `POST` para o endpoint `/analyze-document` com o URI do GCS do seu arquivo.

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze-document' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "gcs_uri": "gs://seu-bucket-aqui/seu-documento.pdf"
}'
```

A API retornará um JSON com os dados extraídos em caso de sucesso.