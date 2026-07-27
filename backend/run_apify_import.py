import os
import sys
import time
from dotenv import load_dotenv

sys.path.append('C:/Users/spcom/Desktop/OttoPinturas1.0/Prospect-On 3.0/backend')

import src.utils.apify_client as apify_module
from src.utils.apify_client import ApifyClient, import_all_regions
from src.utils.database import Database
from src.utils.logger import logger

load_dotenv('C:/Users/spcom/Desktop/OttoPinturas1.0/Prospect-On 3.0/backend/.env')
token = os.getenv('APIFY_API_TOKEN')

def run_import():
    if not token:
        print("Erro: APIFY_API_TOKEN nao encontrado no .env")
        return
    
    print("Iniciando varredura massiva na Apify (continuando a partir da Zona Leste)...")
    
    # Sobrescreve as regioes para pular a Zona Sul e Zona Norte que ja foram feitas
    apify_module.REGIONS = apify_module.REGIONS[2:]
    
    db = Database()
    
    start = time.time()
    try:
        stats = import_all_regions(token=token, db=db, max_per_category=200)
        
        elapsed = (time.time() - start) / 60
        print(f"\n--- IMPORTACAO CONCLUIDA ---")
        print(f"Tempo decorrido: {elapsed:.2f} minutos")
        print(f"Leads importados novos/atualizados: {stats['imported']}")
        print(f"Leads pulados/duplicados: {stats['skipped']}")
        print(f"Total processado: {stats['total']}")
        
    except Exception as e:
        print(f"Erro catastrofico durante a importacao: {e}")

if __name__ == "__main__":
    run_import()
