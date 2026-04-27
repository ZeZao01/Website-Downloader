"""
Gravit Design Factory — Catalog Existing Models
Scans the Asimov folder and catalogs all 32 existing models.
Run: python catalog_existing.py
"""

import os
import json
import uuid
import time
from extractor import extract_metadata_from_html

ASIMOV_DIR = os.path.join(os.path.dirname(__file__), 'Formação AI Designer - Asimov')
CATALOG_FILE = 'models_catalog.json'

DESIGN_SYSTEMS_DIR = os.path.join(ASIMOV_DIR, 'design systems')
REFERENCES_DIR = os.path.join(ASIMOV_DIR, 'referencias')


def catalog_folder(folder, model_type):
    """Scan a folder and return model entries."""
    entries = {}
    if not os.path.isdir(folder):
        print(f"⚠️ Pasta não encontrada: {folder}")
        return entries

    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if not os.path.isdir(path) or name.startswith('.'):
            continue

        index_path = os.path.join(path, 'index.html')
        if not os.path.exists(index_path):
            print(f"  ⚠️ Sem index.html: {name}")
            continue

        print(f"  📄 Processando: {name}")
        try:
            with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
                html = f.read()
            meta = extract_metadata_from_html(html)
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            meta = {'title': name, 'niche': 'general', 'style': 'modern', 'fonts': [], 'colors': []}

        has_ds = os.path.exists(os.path.join(path, 'design-system.html'))

        model_id = str(uuid.uuid4())
        entries[model_id] = {
            'id': model_id,
            'name': meta.get('title') or name,
            'source_url': '',
            'niche': meta.get('niche', 'general'),
            'style': meta.get('style', 'modern'),
            'fonts': meta.get('fonts', []),
            'colors': meta.get('colors', []),
            'zip_path': '',
            'local_path': path,
            'model_type': model_type,
            'has_design_system': has_ds,
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        }
        print(f"    ✅ {meta.get('title', name)} | {meta.get('niche')} | {meta.get('style')}")

    return entries


def main():
    print("=" * 60)
    print("🗂️  Gravit Design Factory — Catalogação de Modelos")
    print("=" * 60)

    catalog = {}
    if os.path.exists(CATALOG_FILE):
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        print(f"📦 Catálogo existente: {len(catalog)} modelos")

    print(f"\n📁 Design Systems: {DESIGN_SYSTEMS_DIR}")
    ds_entries = catalog_folder(DESIGN_SYSTEMS_DIR, 'design_system')
    catalog.update(ds_entries)
    print(f"   → {len(ds_entries)} modelos catalogados")

    print(f"\n📁 Referências: {REFERENCES_DIR}")
    ref_entries = catalog_folder(REFERENCES_DIR, 'reference')
    catalog.update(ref_entries)
    print(f"   → {len(ref_entries)} modelos catalogados")

    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"✅ Total: {len(catalog)} modelos no catálogo")
    print(f"💾 Salvo em: {CATALOG_FILE}")


if __name__ == '__main__':
    main()
