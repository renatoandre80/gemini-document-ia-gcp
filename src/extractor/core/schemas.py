from pydantic import BaseModel, Field
from typing import Optional


class NFeNFSeSchema(BaseModel):
    """
    Schema unificado para dados extraídos de documentos fiscais brasileiros (NF-e e NFS-e),
    usado para guiar a saída estruturada do modelo de IA.
    """
    
    nationalEconomicActivityCode: Optional[str] = Field(alias="Código Nacional de Atividade Econômica (CNAE).", default=None)
    serviceListItem: Optional[str] = Field(alias="Item da lista de serviços (LC 116/2003).", default=None)
    nfeNumber: Optional[str] = Field(alias="Número da Nota Fiscal de Produto (NF-e).", default=None)
    nfeSerie: Optional[str] = Field(alias="Série da NF-e.", default=None)
    totalProductsValue: Optional[float] = Field(alias="Valor total dos produtos.", default=None)
    icmsValue: Optional[float] = Field(alias="Valor do imposto ICMS.", default=None)
    
    
    class Config:
        populate_by_name = True