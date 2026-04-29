
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Erro: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não encontrados no .env")
    exit(1)

supabase: Client = create_client(url, key)

def create_buckets():
    buckets = ["model-previews", "model-zips", "project-uploads", "adaptation-outputs"]
    print("📦 Criando buckets de storage...")
    
    for bucket_name in buckets:
        try:
            # Check if bucket exists
            res = supabase.storage.get_bucket(bucket_name)
            print(f"  ✅ Bucket '{bucket_name}' já existe.")
        except Exception:
            try:
                supabase.storage.create_bucket(bucket_name, options={"public": True})
                print(f"  🆕 Bucket '{bucket_name}' criado com sucesso.")
            except Exception as e:
                print(f"  ❌ Erro ao criar bucket '{bucket_name}': {e}")

if __name__ == "__main__":
    create_buckets()
    print("\n🚀 Configuração de storage concluída!")
    print("⚠️  Lembre-se: Para as tabelas SQL, você deve executar o script SQL no Dashboard do Supabase (SQL Editor).")
