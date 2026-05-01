
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseDB:
    def __init__(self):
        self._init_client()

    def _init_client(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            self.client = None
            self.last_error = f"Missing vars. URL: {bool(url)}, KEY: {bool(key)}"
            print("⚠️ Supabase credentials missing")
        else:
            try:
                self.client: Client = create_client(url, key)
                self.last_error = None
                print("✅ Supabase client initialized")
            except Exception as e:
                self.client = None
                self.last_error = f"Init Exception: {str(e)}"
                print(f"❌ Failed to initialize Supabase: {e}")

    @property
    def is_ready(self):
        if not self.client:
            self._init_client()
        return self.client is not None

    def get_models(self):
        if not self.client: return []
        try:
            res = self.client.table("models").select("*").order("last_captured_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def get_model(self, model_id):
        if not self.client: return None
        try:
            res = self.client.table("models").select("*").eq("id", model_id).single().execute()
            return res.data
        except Exception as e:
            print(f"Error fetching model {model_id}: {e}")
            return None

    def get_model_by_url(self, url):
        if not self.client: return None
        try:
            res = self.client.table("models").select("*").eq("url", url).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Error fetching model by url: {e}")
            return None

    def upsert_model(self, model_data):
        if not self.client: return None
        try:
            # Ensure JSON-serializable fields
            safe_data = self._sanitize_for_supabase(model_data)
            url = safe_data.get("url")
            existing = self.get_model_by_url(url) if url else None
            
            if existing:
                res = self.client.table("models").update(safe_data).eq("id", existing["id"]).execute()
            else:
                res = self.client.table("models").upsert(safe_data).execute()
            return res.data
        except Exception as e:
            print(f"Error upserting model: {e}")
            return None

    def update_model_design_system(self, model_id, design_system_data):
        """Safely update only the design system fields for a model."""
        if not self.client: return None
        try:
            import json
            update = {
                'design_system': json.loads(json.dumps(design_system_data, default=str)),
                'has_design_system': True,
            }
            res = self.client.table("models").update(update).eq("id", model_id).execute()
            return res.data
        except Exception as e:
            print(f"Error updating design system for {model_id}: {e}")
            return None

    def _sanitize_for_supabase(self, data):
        """Ensure all values are JSON-serializable for Supabase."""
        import json
        safe = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                try:
                    # Round-trip through JSON to ensure serializability
                    safe[k] = json.loads(json.dumps(v, default=str))
                except (TypeError, ValueError):
                    safe[k] = str(v)
            elif isinstance(v, set):
                safe[k] = list(v)
            else:
                safe[k] = v
        return safe

    def delete_model(self, model_id):
        if not self.client: return False
        try:
            self.client.table("models").delete().eq("id", model_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting model: {e}")
            return False

    def save_project(self, project_data):
        if not self.client: return None
        try:
            safe_data = self._sanitize_for_supabase(project_data)
            res = self.client.table("projects").insert(safe_data).execute()
            return res.data
        except Exception as e:
            print(f"Error saving project: {e}")
            return None

    def update_project(self, project_id, update_data):
        if not self.client: return None
        try:
            safe_data = self._sanitize_for_supabase(update_data)
            res = self.client.table("projects").update(safe_data).eq("id", project_id).execute()
            return res.data
        except Exception as e:
            print(f"Error updating project: {e}")
            return None

    def get_last_active_project(self):
        """Recover the most recent project that isn't finished."""
        if not self.client: return None
        try:
            res = self.client.table("projects").select("*").neq("status", "completed").order("created_at", desc=True).limit(1).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Error recovering project: {e}")
            return None

    def upload_file(self, bucket, remote_path, local_path):
        if not self.client: return None
        try:
            with open(local_path, 'rb') as f:
                file_data = f.read()
            # Try upload, handling potential "already exists" errors
            try:
                self.client.storage.from_(bucket).upload(remote_path, file_data, {"content-type": "application/zip", "upsert": "true"})
            except Exception as upload_err:
                err_str = str(upload_err).lower()
                if 'duplicate' in err_str or 'already exists' in err_str:
                    # File already exists, update it
                    try:
                        self.client.storage.from_(bucket).update(remote_path, file_data, {"content-type": "application/zip"})
                    except Exception:
                        pass  # Best effort
                else:
                    raise
            return self.client.storage.from_(bucket).get_public_url(remote_path)
        except Exception as e:
            print(f"Error uploading file to {bucket}: {e}")
            return None

    def save_adaptation(self, adaptation_data):
        """Save an adaptation record."""
        if self.client:
            try:
                safe_data = self._sanitize_for_supabase(adaptation_data)
                res = self.client.table("adaptations").insert(safe_data).execute()
                return res.data
            except Exception as e:
                print(f"⚠️ Supabase adaptations save failed ({e}), using local fallback")
        # Local JSON fallback
        return self._save_local_adaptation(adaptation_data)

    def get_adaptations(self, limit=50):
        """Get adaptation history."""
        if self.client:
            try:
                res = (self.client.table("adaptations")
                       .select("*")
                       .order("created_at", desc=True)
                       .limit(limit)
                       .execute())
                return res.data
            except Exception as e:
                print(f"⚠️ Supabase adaptations fetch failed ({e}), using local fallback")
        return self._get_local_adaptations(limit)

    def _save_local_adaptation(self, data):
        path = os.path.join('outputs', '_history.json')
        history = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.insert(0, data)
        history = history[:200]  # keep last 200
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return data

    def _get_local_adaptations(self, limit=50):
        path = os.path.join('outputs', '_history.json')
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[:limit]
        except Exception:
            return []

db = SupabaseDB()
