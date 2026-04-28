import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega chaves do .env
load_dotenv()

def test_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"🔗 Testando conexão com: {url}")
    print(f"🔑 Chave (Role): {key[:10]}...{key[-10:]}")
    
    try:
        supabase: Client = create_client(url, key)
        # Tenta buscar os modelos
        res = supabase.table("models").select("count", count="exact").limit(1).execute()
        print(f"✅ Conexão bem sucedida!")
        print(f"📊 Total de modelos encontrados no banco: {res.count}")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

if __name__ == "__main__":
    test_connection()
