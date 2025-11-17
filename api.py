import os
import json
from fastapi import FastAPI, HTTPException, status, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.extractor.core.gemini_extractor import GeminiDataExtractor
from src.extractor.core.ocr_processor import GoogleDocumentOcr

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração e Validação ---
# É uma boa prática carregar a configuração uma vez na inicialização
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us")
OCR_PROCESSOR_ID = os.getenv("OCR_PROCESSOR_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([PROJECT_ID, OCR_PROCESSOR_ID, GEMINI_API_KEY]):
    raise RuntimeError(
        "Variáveis de ambiente essenciais (PROJECT_ID, OCR_PROCESSOR_ID, GEMINI_API_KEY) não foram definidas."
    )

# --- Inicialização dos Serviços ---
try:
    ocr_service = GoogleDocumentOcr(PROJECT_ID, LOCATION, OCR_PROCESSOR_ID)
    gemini_service = GeminiDataExtractor(GEMINI_API_KEY)
except Exception as e:
    # Se a inicialização falhar, a aplicação não deve iniciar.
    raise RuntimeError(f"Falha ao inicializar os serviços: {e}") from e


# --- Definição da API ---
app = FastAPI(
    title="Document AI OCR with Gemini",
    description="API para extrair e estruturar dados de documentos usando Google Document AI e Gemini.",
    version="1.0.0",
)


class DocumentRequest(BaseModel):
    """Modelo de dados para a requisição de análise de documento."""

    gcs_uri: str = Field(
        ...,
        example="gs://seu-bucket-aqui/NF_SIMPLES.pdf",
        description="O URI do Google Cloud Storage para o arquivo PDF a ser processado.",
    )


@app.post("/analyze-document", status_code=status.HTTP_200_OK)
async def analyze_document_from_gcs(request: DocumentRequest = Body(...)):
    """
    Recebe o URI de um documento no GCS, realiza o OCR e extrai dados estruturados com Gemini.
    """
    print(f"Iniciando análise para o documento: {request.gcs_uri}")

    try:
        # 1. Etapa de OCR a partir do GCS
        # Usando o método correto para processar a partir de um GCS URI
        extracted_text = ocr_service.extract_text_from_gcs_uri(request.gcs_uri)

        if not extracted_text:
            print(f"Falha no OCR para {request.gcs_uri}. O texto extraído está vazio.")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A etapa de OCR não retornou texto. Verifique o documento ou o processador.",
            )

        # 2. Etapa de Extração com Gemini
        structured_data_str = gemini_service.extract_from_text(
            text_content=extracted_text,
        )

        if not structured_data_str:
            print(f"Falha na extração com Gemini para {request.gcs_uri}.")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A etapa de extração com Gemini não retornou dados estruturados.",
            )

        # Converte a string JSON em um objeto Python para o retorno da API
        structured_data_json = json.loads(structured_data_str)

        print(f"✅ Análise concluída com sucesso para {request.gcs_uri}")
        return structured_data_json

    except FileNotFoundError as e:
        # Este erro pode ser lançado pelo Document AI se o URI do GCS for inválido ou inacessível
        print(f"Erro de arquivo não encontrado para {request.gcs_uri}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"O arquivo não foi encontrado no GCS: {request.gcs_uri}. Verifique o URI e as permissões.")
    except Exception as e:
        print(f"Erro inesperado durante o processamento de {request.gcs_uri}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno no servidor: {e}",
        )