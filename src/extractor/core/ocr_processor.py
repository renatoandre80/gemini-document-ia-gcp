from google.cloud import documentai
from typing import Optional
import os


class GoogleDocumentOcr:
    """
    Classe focada exclusivamente em realizar OCR em documentos (PDFs, Imagens)
    usando o processador 'Document OCR' do Google Cloud.
    
    ### Variáveis de Ambiente Necessárias:
    - GOOGLE_APPLICATION_CREDENTIALS: Caminho para o arquivo JSON da chave da conta de serviço.
    
    ### Suporte a Tipos de Arquivo:
    - PDF, JPG, JPEG, PNG
    
    ### Saída:
    - Retorna o texto extraído como uma string.
    """
    
    MIME_TYPE_MAPPING = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }

    def __init__(self, project_id: str, location: str, ocr_processor_id: str):
        """
        Inicializa o serviço de OCR.
        """
        
        if not all([project_id, location, ocr_processor_id]):
            raise ValueError("Project ID, location, and OCR Processor ID are required.")

        self.client = documentai.DocumentProcessorServiceClient(
            client_options={"api_endpoint": f"{location}-documentai.googleapis.com"}
        )
        self.processor_name = self.client.processor_path(
            project_id, location, ocr_processor_id
        )

    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Processa um arquivo e extrai todo o seu conteúdo de texto."""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        _, file_extension = os.path.splitext(file_path)
        mime_type = self.MIME_TYPE_MAPPING.get(file_extension.lower())

        if not mime_type:
            supported = ", ".join(self.MIME_TYPE_MAPPING.keys())
            raise ValueError(f"Unsupported file type: '{file_extension}'. Supported: {supported}")

        try:
            with open(file_path, "rb") as document_file:
                file_content = document_file.read()

            raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
            request = documentai.ProcessRequest(name=self.processor_name, raw_document=raw_document)

            print(f"Iniciando OCR no arquivo '{os.path.basename(file_path)}'...")
            result = self.client.process_document(request=request)
            
            return result.document.text
        
        except Exception as e:
            print(f"Ocorreu um erro durante o OCR no Document AI: {e}")
            return None