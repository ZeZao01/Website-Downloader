import json
import os
import sys

# Adiciona a pasta raiz ao path para encontrar o database.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import db
from dotenv import load_dotenv

load_dotenv()

def migrate():
    CATALOG_FILE = 'models_catalog.json'
    
    if not os.path.exists(CATALOG_FILE):
        print(f"❌ Arquivo {CATALOG_FILE} não encontrado.")
        return

    with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"📦 Carregando {len(catalog)} modelos do JSON...")
    
    count = 0
    for model_id, data in catalog.items():
        try:
            # Prepara os dados para o Supabase
            model_data = {
                'id': data.get('id', model_id),
                'name': data.get('name', 'Sem nome'),
                'niche': data.get('niche', 'general'),
                'style': data.get('style', 'modern'),
                'fonts': data.get('fonts', []),
                'colors': data.get('colors', []),
                'metadata': data,
                'has_design_system': data.get('has_design_system', False),
                'created_at': data.get('created_at')
            }
            
            db.upsert_model(model_data)
            count += 1
            if count % 20 == 0:
                print(f"  ☁️ {count} modelos sincronizados...")
                
        except Exception as e:
            print(f"  ❌ Erro ao subir {data.get('name')}: {e}")

    print(f"✅ Sincronização concluída! {count} modelos estão agora no Supabase.")

if __name__ == "__main__":
    migrate()
