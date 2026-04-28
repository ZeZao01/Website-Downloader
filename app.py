"""
Gravit Design Factory — Main Application
4-stage design system capture, extraction, upload, and adaptation pipeline
with password-gate security and anti-hack protections.
"""

from flask import (Flask, render_template, request, send_file, Response,
                   jsonify, session, redirect, url_for, abort)
from functools import wraps
import os
import shutil
import uuid
import queue
import threading
import time
import gc
import json
import hashlib
import zipfile
import requests
from collections import defaultdict
from dotenv import load_dotenv
from downloader import WebsiteDownloader, zip_directory, get_site_name
from extractor import DesignSystemExtractor, extract_metadata_from_html
from adapter import StructureAdapter, extract_zip_project, create_output_zip
from database import db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'gdf-fallback-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# ─── Security Config ───
PASSWORD_HASH = hashlib.sha256(
    os.getenv('DESIGN_FACTORY_PASSWORD', '').encode()
).hexdigest()
MAX_AUTH_ATTEMPTS = 5
LOCKOUT_SECONDS = 1800  # 30 minutes
auth_attempts = defaultdict(lambda: {'count': 0, 'locked_until': 0})
auth_lock = threading.Lock()

# ─── Folders ───
DOWNLOAD_FOLDER = 'downloads'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
for folder in [DOWNLOAD_FOLDER, UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ─── Session TTLs ───
COMPLETE_TTL = 1800
ERROR_TTL = 600
PROCESSING_TTL = 1800
ORPHAN_FILE_TTL = 1800
CLEANUP_INTERVAL = 300

# ─── In-memory state ───
message_queues = {}
download_results = {}
session_lock = threading.Lock()

# ─── Models catalog handled by database.py ───


# ═══════════════════════════════════════════
# SECURITY: Password Gate & Anti-Hack
# ═══════════════════════════════════════════

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'"
    )
    return response


def _get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '0.0.0.0').split(',')[0].strip()


def _check_lockout(ip):
    with auth_lock:
        info = auth_attempts[ip]
        if info['locked_until'] > time.time():
            return True, int(info['locked_until'] - time.time())
        return False, 0


def _record_attempt(ip, success):
    with auth_lock:
        if success:
            auth_attempts[ip] = {'count': 0, 'locked_until': 0}
        else:
            auth_attempts[ip]['count'] += 1
            if auth_attempts[ip]['count'] >= MAX_AUTH_ATTEMPTS:
                auth_attempts[ip]['locked_until'] = time.time() + LOCKOUT_SECONDS


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'unauthorized', 'redirect': '/'}), 401
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@app.route('/auth', methods=['POST'])
def authenticate():
    ip = _get_client_ip()
    locked, remaining = _check_lockout(ip)
    if locked:
        return jsonify({
            'success': False,
            'locked': True,
            'remaining': remaining,
            'message': f'Acesso bloqueado. Tente novamente em {remaining // 60} minutos.'
        }), 429

    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    if pwd_hash == PASSWORD_HASH:
        _record_attempt(ip, True)
        session['authenticated'] = True
        session.permanent = True
        return jsonify({'success': True})
    else:
        _record_attempt(ip, False)
        with auth_lock:
            attempts_left = MAX_AUTH_ATTEMPTS - auth_attempts[ip]['count']
        msg = 'Senha incorreta.'
        if attempts_left <= 2:
            msg += f' {attempts_left} tentativa(s) restante(s).'
        return jsonify({'success': False, 'message': msg, 'attempts_left': attempts_left}), 403


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


# ═══════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════

@app.route('/')
def index():
    # Recovery Memory: Check for last active project
    active_project = db.get_last_active_project()
    if active_project and not session.get('project_id'):
        session['project_id'] = active_project['id']
    
    return render_template('index.html', active_project=active_project)


@app.route('/api/sync_session', methods=['POST'])
@require_auth
def sync_session():
    data = request.get_json() or {}
    project_id = data.get('project_id')
    if project_id:
        session['project_id'] = project_id
        return jsonify({'success': True})
    return jsonify({'success': False}), 400


@app.route('/health')
def health():
    info = {'status': 'ok'}
    with session_lock:
        info['sessions'] = len(download_results)
    models = db.get_models()
    info['models'] = len(models) if models else 0
    return jsonify(info)


# ═══════════════════════════════════════════
# STAGE 1: Site Capture
# ═══════════════════════════════════════════

@app.route('/api/capture', methods=['POST'])
@require_auth
def start_capture():
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    sid = str(uuid.uuid4())
    now = time.time()
    with session_lock:
        message_queues[sid] = queue.Queue()
        download_results[sid] = {
            'status': 'processing', 'zip_path': None,
            'filename': None, 'started_at': now,
        }

    thread = threading.Thread(target=_process_capture, args=(sid, url), daemon=True)
    thread.start()
    return jsonify({'session_id': sid})


def _process_capture(sid, url):
    with session_lock:
        q = message_queues.get(sid)
    if not q:
        return

    download_dir = os.path.join(DOWNLOAD_FOLDER, sid)
    zip_path = os.path.join(DOWNLOAD_FOLDER, f"{sid}.zip")

    def log_cb(msg):
        q.put(msg)

    try:
        # --- LÓGICA DE INTELIGÊNCIA / CACHE ---
        q.put("🔍 Verificando histórico de capturas...")
        existing_model = db.get_model_by_url(url)
        
        # Gerar hash do conteúdo atual para comparação
        current_hash = ""
        try:
            resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            current_hash = hashlib.md5(resp.text.encode('utf-8')).hexdigest()
        except:
            pass

        if existing_model:
            old_hash = existing_model.get('content_hash')
            if old_hash == current_hash and current_hash != "":
                q.put("✅ Site identificado no histórico (Sem alterações).")
                q.put("♻️ Recuperando dados do banco de dados...")
                time.sleep(1)
                
                # Simular conclusão rápida usando dados existentes
                with session_lock:
                    download_results[sid] = {
                        'status': 'complete', 
                        'zip_path': existing_model.get('zip_storage_path'),
                        'filename': f"{existing_model.get('name')}.zip", 
                        'model_id': existing_model.get('id'),
                        'created_at': time.time(),
                    }
                q.put("🎉 Dados recuperados com sucesso!")
                return

            q.put("🔄 Update detectado ou site sem hash. Iniciando nova captura...")

        # --- FIM DA LÓGICA DE CACHE ---

        downloader = WebsiteDownloader(url, download_dir, log_callback=log_cb)
        success = downloader.process()

        if not success:
            q.put("❌ Falha na captura")
            with session_lock:
                download_results[sid] = {'status': 'error', 'error': 'Capture failed', 'created_at': time.time()}
            return

        site_name = get_site_name(url)
        zip_filename = f"{site_name}.zip"
        model_id = existing_model['id'] if existing_model else str(uuid.uuid4())

        # Extract metadata for catalog
        index_path = os.path.join(download_dir, 'index.html')
        metadata = {}
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            metadata = extract_metadata_from_html(html_content)

        q.put("📦 Criando arquivo ZIP...")
        zip_directory(download_dir, zip_path)

        q.put("🎉 Captura concluída e catalogada!")
        
        # Upload ZIP to Supabase Storage if possible
        storage_path = None
        if db.client:
            q.put("☁️ Sincronizando com Supabase...")
            storage_path = db.upload_file("model-zips", f"{model_id}.zip", zip_path)

        model_entry = {
            'id': model_id,
            'name': metadata.get('title', site_name),
            'url': url,
            'content_hash': current_hash,
            'niche': metadata.get('niche', 'general'),
            'style': metadata.get('style', 'modern'),
            'fonts': metadata.get('fonts', []),
            'colors': metadata.get('colors', []),
            'zip_storage_path': storage_path or zip_path,
            'metadata': metadata,
            'last_captured_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'has_design_system': False,
        }
        db.upsert_model(model_entry)

        if os.path.isdir(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
        with session_lock:
            download_results[sid] = {
                'status': 'complete', 'zip_path': zip_path,
                'filename': zip_filename, 'model_id': model_id,
                'project_id': project_id,
                'created_at': time.time(),
            }
        
        # PERSISTENT MEMORY: Save Project
        project_id = str(uuid.uuid4())
        db.save_project({
            'id': project_id,
            'name': f"Captura: {metadata.get('title', site_name)}",
            'status': 'captured',
            'design_system_id': model_id,
            'original_structure': {'url': url, 'sid': sid},
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%S')
        })
        # session['project_id'] = project_id # REMOVIDO: Causa erro de contexto no background thread
        
        # Envia o project_id via mensagem para o frontend salvar
        q.put(f"COMPLETE_DATA|{json.dumps({'model_id': model_id, 'project_id': project_id})}")
    except Exception as e:
        q.put(f"❌ Erro: {str(e)}")
        with session_lock:
            download_results[sid] = {'status': 'error', 'error': str(e), 'created_at': time.time()}
        for p in [download_dir, zip_path]:
            if os.path.exists(p):
                try:
                    (shutil.rmtree if os.path.isdir(p) else os.remove)(p)
                except Exception:
                    pass
    finally:
        downloader = None
        gc.collect()


@app.route('/stream/<session_id>')
@require_auth
def stream(session_id):
    def generate():
        with session_lock:
            q = message_queues.get(session_id)
        if not q:
            yield "data: ❌ Sessão não encontrada\n\n"
            yield "event: done\ndata: error\n\n"
            return
        deadline = time.time() + 30 * 60
        while True:
            if time.time() > deadline:
                yield "event: done\ndata: timeout\n\n"
                return
            try:
                message = q.get(timeout=30)
                yield f"data: {message}\n\n"
                with session_lock:
                    result = download_results.get(session_id, {})
                if result.get('status') in ('complete', 'error'):
                    extra = json.dumps({
                        'model_id': result.get('model_id', ''),
                        'project_id': result.get('project_id', '')
                    })
                    yield f"event: done\ndata: {result['status']}|{extra}\n\n"
                    return
            except queue.Empty:
                with session_lock:
                    result = download_results.get(session_id, {})
                if result.get('status') in ('complete', 'error'):
                    yield f"event: done\ndata: {result['status']}\n\n"
                    return
                yield ": keepalive\n\n"
    return Response(generate(), mimetype='text/event-stream')


# ═══════════════════════════════════════════
# STAGE 2: Design System Extraction
# ═══════════════════════════════════════════

@app.route('/api/extract-design-system', methods=['POST'])
@require_auth
def extract_design_system():
    data = request.get_json(silent=True) or {}
    model_id = data.get('model_id')
    if not model_id:
        return jsonify({'error': 'model_id required'}), 400

    model = db.get_model(model_id)
    if not model:
        return jsonify({'error': 'Model not found'}), 404

    zip_path = model.get('zip_path') or os.path.join(DOWNLOAD_FOLDER, f"{model_id}.zip")
    if not os.path.exists(zip_path):
        # Try to download from storage if not on disk
        storage_path = model.get('zip_storage_path')
        if storage_path and storage_path.startswith('http'):
            import requests
            r = requests.get(storage_path)
            with open(zip_path, 'wb') as f:
                f.write(r.content)
        else:
            return jsonify({'error': 'Model ZIP not found'}), 404

    try:
        extract_dir = os.path.join(DOWNLOAD_FOLDER, f"extract_{model_id}")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)

        index_path = os.path.join(extract_dir, 'index.html')
        if not os.path.exists(index_path):
            for root, _, files in os.walk(extract_dir):
                for f in files:
                    if f == 'index.html':
                        index_path = os.path.join(root, f)
                        break

        with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()

        extractor = DesignSystemExtractor(html, model.get('source_url', ''))
        ds_data = extractor.extract_all()

        model['design_system'] = ds_data
        model['has_design_system'] = True
        db.upsert_model(model)

        shutil.rmtree(extract_dir, ignore_errors=True)
        return jsonify({'success': True, 'design_system': ds_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════
# STAGE 3: Project Upload
# ═══════════════════════════════════════════

@app.route('/api/upload-project', methods=['POST'])
@require_auth
def upload_project():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename or not file.filename.endswith('.zip'):
        return jsonify({'error': 'Only ZIP files are accepted'}), 400

    project_id = str(uuid.uuid4())
    zip_path = os.path.join(UPLOAD_FOLDER, f"{project_id}.zip")
    file.save(zip_path)

    extract_dir = os.path.join(UPLOAD_FOLDER, project_id)
    extract_zip_project(zip_path, extract_dir)

    structure = {'html': [], 'css': [], 'js': [], 'assets': []}
    for root, _, files in os.walk(extract_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), extract_dir)
            ext = os.path.splitext(f)[1].lower()
            if ext in ('.html', '.htm'):
                structure['html'].append(rel)
            elif ext in ('.css', '.scss'):
                structure['css'].append(rel)
            elif ext in ('.js', '.ts', '.jsx', '.tsx'):
                structure['js'].append(rel)
            elif ext in ('.png', '.jpg', '.svg', '.webp', '.gif'):
                structure['assets'].append(rel)

    return jsonify({
        'success': True,
        'project_id': project_id,
        'structure': structure,
        'file_count': sum(len(v) for v in structure.values()),
    })


@app.route('/api/capture-project', methods=['POST'])
@require_auth
def capture_project():
    """Capture a project from URL (same as stage 1 but for the real project)."""
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    project_id = str(uuid.uuid4())
    download_dir = os.path.join(UPLOAD_FOLDER, project_id)

    try:
        downloader = WebsiteDownloader(url, download_dir)
        success = downloader.process()
        if not success:
            return jsonify({'error': 'Capture failed'}), 500

        structure = {'html': [], 'css': [], 'js': [], 'assets': []}
        for root, _, files in os.walk(download_dir):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), download_dir)
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.html', '.htm'):
                    structure['html'].append(rel)
                elif ext in ('.css', '.scss'):
                    structure['css'].append(rel)
                elif ext in ('.js', '.ts'):
                    structure['js'].append(rel)

        return jsonify({'success': True, 'project_id': project_id, 'structure': structure})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════
# STAGE 4: Adaptation
# ═══════════════════════════════════════════

@app.route('/api/adapt', methods=['POST'])
@require_auth
def adapt_project():
    data = request.get_json(silent=True) or {}
    model_id = data.get('model_id')
    project_id = data.get('project_id')

    if not model_id or not project_id:
        return jsonify({'error': 'model_id and project_id required'}), 400

    model = db.get_model(model_id)
    if not model or not model.get('design_system'):
        return jsonify({'error': 'Model or design system not found'}), 404

    project_dir = os.path.join(UPLOAD_FOLDER, project_id)
    if not os.path.isdir(project_dir):
        return jsonify({'error': 'Project not found'}), 404

    try:
        output_id = str(uuid.uuid4())
        output_dir = os.path.join(OUTPUT_FOLDER, output_id)

        adapter = StructureAdapter(model['design_system'], project_dir)
        adapter.create_adaptation_package(output_dir)

        zip_path = os.path.join(OUTPUT_FOLDER, f"{output_id}.zip")
        create_output_zip(output_dir, zip_path)
        shutil.rmtree(output_dir, ignore_errors=True)

        # Save project to Supabase
        project_entry = {
            'id': project_id,
            'name': f"Adapted from {model.get('name', model_id[:8])}",
            'source_type': 'upload',
            'selected_model_id': model_id,
            'adaptation_status': 'complete',
            'adaptation_result_path': zip_path
        }
        db.save_project(project_entry)

        return jsonify({
            'success': True,
            'output_id': output_id,
            'download_url': f'/api/download-output/{output_id}',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-output/<output_id>')
@require_auth
def download_output(output_id):
    zip_path = os.path.join(OUTPUT_FOLDER, f"{output_id}.zip")
    if not os.path.exists(zip_path):
        return "File not found", 404
    return send_file(zip_path, as_attachment=True, download_name=f"adaptation-{output_id[:8]}.zip")


# ═══════════════════════════════════════════
# MODELS CATALOG API
# ═══════════════════════════════════════════

@app.route('/api/models')
@require_auth
def list_models():
    if not db.is_ready:
        return jsonify({'error': f'❌ Falha Crítica de Inicialização Supabase:\n{getattr(db, "last_error", "Erro Desconhecido")}'})
        
    try:
        models = db.get_models()
        if not models and models != []:
            return jsonify({'error': '❌ O Supabase não retornou dados. Verifique o RLS ou se a tabela "models" existe.'})
        return jsonify(models)
    except Exception as e:
        import traceback
        return jsonify({'error': f'DEBUG: {str(e)}\n{traceback.format_exc()}'}), 500

    models_list = []
    for m in models:
        models_list.append({
            'id': m.get('id'),
            'name': m.get('name', ''),
            'source_url': m.get('source_url', ''),
            'niche': m.get('niche', ''),
            'style': m.get('style', ''),
            'colors': m.get('colors', [])[:5],
            'fonts': m.get('fonts', [])[:3],
            'has_design_system': m.get('has_design_system', False),
            'created_at': m.get('created_at', ''),
        })
    return jsonify(models_list)


@app.route('/api/models/<model_id>')
@require_auth
def get_model(model_id):
    model = db.get_model(model_id)
    if not model:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(model)


@app.route('/api/models/<model_id>/download')
@require_auth
def download_model(model_id):
    model = db.get_model(model_id)
    if not model:
        return "Not found", 404
    zip_path = model.get('zip_path') or os.path.join(DOWNLOAD_FOLDER, f"{model_id}.zip")
    if not os.path.exists(zip_path):
        return "File not found", 404
    name = model.get('name', model_id[:8])
    return send_file(zip_path, as_attachment=True, download_name=f"{name}.zip")


@app.route('/api/models/<model_id>', methods=['DELETE'])
@require_auth
def delete_model(model_id):
    model = db.get_model(model_id)
    if not model:
        return jsonify({'error': 'Not found'}), 404
    
    db.delete_model(model_id)
    
    zip_path = model.get('zip_path')
    if zip_path and os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except Exception:
            pass
    return jsonify({'success': True})


# ═══════════════════════════════════════════
# LEGACY: Direct download (keep compatibility)
# ═══════════════════════════════════════════

@app.route('/download-file/<session_id>')
@require_auth
def download_file(session_id):
    with session_lock:
        result = download_results.get(session_id)
    if not result or result.get('status') != 'complete':
        return "File not ready", 404
    zip_path = result['zip_path']
    filename = result['filename']
    if not zip_path or not os.path.exists(zip_path):
        return "File not found", 404
    return send_file(zip_path, as_attachment=True, download_name=filename)


# ═══════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════

def _purge_session(session_id):
    with session_lock:
        result = download_results.pop(session_id, None)
        message_queues.pop(session_id, None)
    if not result:
        return
    zip_path = result.get('zip_path')
    if zip_path and os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except Exception:
            pass


def cleanup_loop():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        try:
            now = time.time()
            to_remove = []
            with session_lock:
                snapshot = list(download_results.items())
            for sid, result in snapshot:
                status = result.get('status')
                created = result.get('created_at', 0)
                if not created:
                    continue
                age = now - created
                if status == 'complete' and age > COMPLETE_TTL:
                    to_remove.append(sid)
                elif status == 'error' and age > ERROR_TTL:
                    to_remove.append(sid)
                elif status == 'processing' and age > PROCESSING_TTL:
                    to_remove.append(sid)
            for sid in to_remove:
                _purge_session(sid)
            gc.collect()
        except Exception:
            pass


threading.Thread(target=cleanup_loop, daemon=True).start()


if __name__ == '__main__':
    app.run(debug=True, port=5001, threaded=True)
