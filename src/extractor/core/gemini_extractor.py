from .schemas import NFeNFSeSchema
from google.genai import types
from google import genai


class GeminiDataExtractor:
    """
    Utiliza a API do Gemini com Saída Estruturada para extrair dados
    de um texto em um schema Pydantic definido.
    """
    
    def __init__(self, gemini_api_key: str):
        if not gemini_api_key:
            raise ValueError("Gemini API Key is required.")
        
        self.gemini_client = genai.Client(api_key=gemini_api_key)

    def extract_from_text(self, text_content: str) -> NFeNFSeSchema:
        """
        Recebe um texto e extrai os dados de acordo com o schema Pydantic.
        
        ### Parâmetros:
        - `text_content`: Texto extraído via OCR.
        
        ### Retorna:
        - Dados validados no formato do schema NFeNFSeSchema.
        
        ### Exceções:
        - Retorna None em caso de falha na extração ou validação.
        """
        
        prompt = f"""
        Analise o texto de um documento fiscal brasileiro abaixo.
        Primeiro, identifique se é uma Nota Fiscal de Produto (NF-e) ou de Serviço (NFS-e).
        Depois, extraia as informações relevantes para preencher a estrutura de dados solicitada.

        Texto para análise:
        ---
        
        {text_content}
        
        ---
        """
        
        try:
            print("Enviando texto para o Gemini para extração estruturada...")
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    response_mime_type="application/json",
                    response_schema=NFeNFSeSchema,
                    temperature=0
                )
            )
            
            validated_data = NFeNFSeSchema.model_validate_json(response.text)
            return validated_data.model_dump_json(by_alias=True, indent=2, exclude_none=False)
            
        except Exception as e:
            print(f"Ocorreu um erro ao extrair dados com o Gemini: {e}")
            return None