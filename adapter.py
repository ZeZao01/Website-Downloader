"""
Gravit Design Factory — Structure Adapter
Maps extracted design system onto a real project,
generating adapted code + orientation guide.
"""

import os
import re
import json
import zipfile
import shutil
import tempfile
from bs4 import BeautifulSoup


class StructureAdapter:
    """Adapts a real project's structure using an extracted design system."""

    def __init__(self, design_system_data, project_dir, log_callback=None):
        self.ds = design_system_data
        self.project_dir = project_dir
        self.log = log_callback or (lambda m: print(m))
        self.mappings = {}
        self.guide_lines = []

    def analyze_project(self):
        """Scan project structure and identify files to adapt."""
        self.log("🔍 Analisando estrutura do projeto...")
        structure = {'html': [], 'css': [], 'js': [], 'assets': [], 'other': []}

        for root, dirs, files in os.walk(self.project_dir):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.next'}]
            for f in files:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, self.project_dir)
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.html', '.htm'):
                    structure['html'].append(rel)
                elif ext in ('.css', '.scss', '.less'):
                    structure['css'].append(rel)
                elif ext in ('.js', '.ts', '.jsx', '.tsx'):
                    structure['js'].append(rel)
                elif ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'):
                    structure['assets'].append(rel)
                else:
                    structure['other'].append(rel)

        self.log(f"   📄 {len(structure['html'])} HTML, {len(structure['css'])} CSS, "
                 f"{len(structure['js'])} JS, {len(structure['assets'])} assets")
        return structure

    def generate_css_variables(self):
        """Generate CSS custom properties from the design system."""
        self.log("🎨 Gerando CSS variables do design system...")
        lines = [':root {']

        colors = self.ds.get('colors', [])
        hex_colors = [c for c in colors if c.startswith('#')]
        tw_colors = [c for c in colors if c.startswith('tw:')]

        for i, color in enumerate(hex_colors[:15]):
            lines.append(f'  --ds-color-{i + 1}: {color};')

        fonts = self.ds.get('fonts', [])
        for i, font in enumerate(fonts[:3]):
            clean = font.replace("'", "").replace('"', '').strip()
            lines.append(f'  --ds-font-{i + 1}: "{clean}", sans-serif;')

        lines.append('}')
        lines.append('')

        # Add Tailwind class comments as reference
        if tw_colors:
            lines.append('/* Tailwind classes from design system:')
            for tc in tw_colors[:20]:
                lines.append(f'   {tc.replace("tw:", "")}')
            lines.append('*/')

        return '\n'.join(lines)

    def generate_adaptation_guide(self, structure):
        """Generate a markdown guide for the adaptation."""
        self.log("📝 Gerando guia de adaptação...")
        guide = []
        guide.append(f"# Guia de Adaptação — {self.ds.get('title', 'Design System')}")
        guide.append('')
        guide.append('## 1. Tipografia')
        guide.append('')
        for t in self.ds.get('typography', [])[:8]:
            guide.append(f"- **{t['tag'].upper()}**: `{t['classes']}`")
            guide.append(f"  Exemplo: \"{t['sample_text'][:60]}\"")
        guide.append('')

        guide.append('## 2. Cores & Superfícies')
        guide.append('')
        colors = self.ds.get('colors', [])
        for c in colors[:15]:
            guide.append(f"- `{c}`")
        guide.append('')

        if self.ds.get('gradients'):
            guide.append('### Gradientes')
            for g in self.ds['gradients'][:5]:
                guide.append(f"- `{g[:100]}`")
            guide.append('')

        guide.append('## 3. Componentes')
        guide.append('')
        comps = self.ds.get('components', {})
        for comp_type, items in comps.items():
            if items:
                guide.append(f"### {comp_type.title()} ({len(items)})")
                for item in items[:3]:
                    guide.append(f"- Classes: `{item.get('classes', '')}`")
                guide.append('')

        guide.append('## 4. Layout')
        guide.append('')
        for l in self.ds.get('layout', [])[:5]:
            guide.append(f"- `<{l['tag']}>` → `{l['classes']}`")
        guide.append('')

        guide.append('## 5. Motion & Animações')
        guide.append('')
        motion = self.ds.get('motion', {})
        for kf in motion.get('keyframes', []):
            guide.append(f"- `@keyframes {kf['name']}`")
        guide.append('')

        guide.append('## 6. Estrutura do Projeto')
        guide.append('')
        guide.append('### Arquivos HTML')
        for f in structure.get('html', []):
            guide.append(f"- `{f}`")
        guide.append('')
        guide.append('### Arquivos CSS')
        for f in structure.get('css', []):
            guide.append(f"- `{f}`")
        guide.append('')

        guide.append('## 7. Instruções de Implementação')
        guide.append('')
        guide.append('1. Copie `design-system-variables.css` para o diretório de estilos do projeto')
        guide.append('2. Importe as variáveis no arquivo CSS principal')
        guide.append('3. Substitua as classes de estilo conforme o mapeamento acima')
        guide.append('4. Ajuste os componentes usando os exemplos do `design-system.html`')
        guide.append('5. Teste responsividade e animações')

        return '\n'.join(guide)

    def create_adaptation_package(self, output_dir):
        """Create the full adaptation package."""
        self.log("📦 Criando pacote de adaptação...")
        os.makedirs(output_dir, exist_ok=True)

        structure = self.analyze_project()

        # 1. CSS Variables
        css_vars = self.generate_css_variables()
        css_path = os.path.join(output_dir, 'design-system-variables.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_vars)

        # 2. Adaptation Guide
        guide = self.generate_adaptation_guide(structure)
        guide_path = os.path.join(output_dir, 'adaptation-guide.md')
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)

        # 3. Design System Data (JSON)
        data_path = os.path.join(output_dir, 'design-system-data.json')
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(self.ds, f, indent=2, ensure_ascii=False)

        # 4. Copy project files
        project_out = os.path.join(output_dir, 'project')
        if os.path.exists(self.project_dir):
            shutil.copytree(self.project_dir, project_out, dirs_exist_ok=True)

        self.log(f"✅ Pacote gerado em {output_dir}")
        return output_dir


def extract_zip_project(zip_path, extract_to):
    """Extract a uploaded ZIP file to a directory."""
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_to)
    return extract_to


def create_output_zip(source_dir, output_path):
    """Create a ZIP from the adaptation output."""
    base = output_path.replace('.zip', '')
    shutil.make_archive(base, 'zip', source_dir)
    return base + '.zip'
