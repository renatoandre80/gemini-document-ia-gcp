from src.extractor.core.gemini_extractor import GeminiDataExtractor
from src.extractor.core.ocr_processor import GoogleDocumentOcr
from dotenv import load_dotenv
import os


def run(file_path: str):
    """
    Orquestra o pipeline completo: OCR -> Extração Estruturada.
    
    ### Parâmetros:
    - file_path: Caminho para o arquivo PDF ou imagem a ser processado.
    
    ### Pré-requisitos:
    - Variáveis de ambiente no arquivo `.env`:
    
        - PROJECT_ID: ID do projeto Google Cloud.
        - LOCATION: Localização do processador (ex: "us").
        - OCR_PROCESSOR_ID: ID do processador de OCR do Document AI.
        - GEMINI_API_KEY: Chave de API para o Gemini.
        
    ### Saídas:
    - Texto bruto extraído salvo em `output/{nome_arquivo}_ocr_output.txt`.
    - Dados estruturados em JSON salvo em `output/{nome_arquivo}_structured_output.json`.
    - Logs no console detalhando cada etapa do processo.
    """
    
    load_dotenv()
    
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION", "us")
    OCR_PROCESSOR_ID = os.getenv("OCR_PROCESSOR_ID")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not all([PROJECT_ID, OCR_PROCESSOR_ID, GEMINI_API_KEY]):
        print("Erro: Verifique se as variáveis PROJECT_ID, OCR_PROCESSOR_ID e GEMINI_API_KEY estão no arquivo .env")
        return

    # Garante que o diretório de saída exista
    os.makedirs("output", exist_ok=True)

    try:
        # 2. Instancia os Serviços
        ocr_service = GoogleDocumentOcr(PROJECT_ID, LOCATION, OCR_PROCESSOR_ID)
        gemini_service = GeminiDataExtractor(GEMINI_API_KEY)
        
        # 3. Etapa de OCR
        extracted_text = ocr_service.extract_text_from_file(file_path)

        if not extracted_text:
            print("Pipeline interrompido: falha na etapa de OCR.")
            return

        # salva o texto bruto para depuracao
        file_name_only = os.path.basename(file_path)
        base_name = os.path.splitext(file_name_only)[0]
        with open(f"output/{base_name}_ocr_output.txt", 'w', encoding='utf-8') as f:
            f.write(extracted_text)
            
        print(f"Texto bruto do OCR salvo em '{base_name}_ocr_output.txt'")

        structured_data = gemini_service.extract_from_text(
            text_content=extracted_text, 
        )

        if structured_data:
            print("\n✅ Sucesso! Dados estruturados e validados pelo Gemini:")
            print(structured_data)

            # Salva o JSON estruturado em um arquivo
            with open(f"output/{base_name}_structured_output.json", 'w', encoding='utf-8') as f:
                f.write(structured_data)
                
            print(f"Dados estruturados salvos em '{base_name}_structured_output.json'")

    except (ValueError, FileNotFoundError) as e:
        print(f"\nErro: {e}")


if __name__ == '__main__':
    pdf_to_process = r'C:/Users/renat/OneDrive/Área de Trabalho/estudos/ocr_documentAI/examples/NF_SIMPLES.pdf'
    run(pdf_to_process)