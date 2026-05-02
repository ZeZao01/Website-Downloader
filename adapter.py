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
import requests


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

    def generate_ai_adaptation_plan(self, structure):
        """Use AI to generate a detailed adaptation plan (Groq or OpenAI)."""
        # Determine which AI provider to use
        openai_key = os.getenv('OPENAI_API_KEY', '')
        groq_key = os.getenv('GROQ_API_KEY', '')

        # Detect OpenRouter keys (sk-or-v1-...) — they don't work on api.openai.com
        is_real_openai = openai_key and openai_key.startswith('sk-') and not openai_key.startswith('sk-or-')

        if is_real_openai:
            api_key = openai_key
            api_url = "https://api.openai.com/v1/chat/completions"
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            provider_name = "OpenAI"
        elif groq_key:
            api_key = groq_key
            api_url = "https://api.groq.com/openai/v1/chat/completions"
            model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
            provider_name = "Groq"
        else:
            self.log("⚠️ Nenhuma API key válida configurada (OpenAI/Groq). Pulando plano de IA.")
            return None

        self.log(f"🤖 Solicitando plano de adaptação inteligente via {provider_name}...")
        
        # Limit the JSON size to avoid hitting token limits or timeouts
        structure_str = json.dumps(structure, indent=2)
        if len(structure_str) > 5000:
            structure_str = structure_str[:5000] + "\n... (truncated)"

        prompt = f"""You are a senior frontend architect. 
Adapt the following Design System to the structure of the Real Project.

DESIGN SYSTEM:
{json.dumps(self.ds, indent=2)[:3000]}

PROJECT STRUCTURE:
{structure_str}

TASK:
1. Map the Design System components (buttons, cards, inputs) to the project files.
2. Provide specific code snippets to replace classes in the project.
3. Suggest a new CSS architecture based on the design system variables.

Return a detailed markdown report."""

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
            res = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                self.log(f"✅ Plano de IA gerado com sucesso via {provider_name}.")
                return res.json()['choices'][0]['message']['content']
            else:
                error_detail = ''
                try:
                    error_detail = res.json().get('error', {}).get('message', res.text[:200])
                except Exception:
                    error_detail = res.text[:200]
                self.log(f"⚠️ Erro na API {provider_name} ({res.status_code}): {error_detail}")
        except Exception as e:
            self.log(f"❌ Falha na chamada de IA ({provider_name}): {e}")
        return None

    def _build_css_block(self):
        """Return CSS variables as a string for embedding in prompts."""
        return self.generate_css_variables()

    def _build_colors_summary(self):
        colors = self.ds.get('colors', [])
        hex_c = [c for c in colors if c.startswith('#')][:10]
        return ', '.join(hex_c) if hex_c else 'Não definido'

    def _build_fonts_summary(self):
        fonts = self.ds.get('fonts', [])[:3]
        return ', '.join(fonts) if fonts else 'sans-serif'

    def _build_components_summary(self):
        comps = self.ds.get('components', {})
        parts = []
        for k, v in comps.items():
            if v:
                parts.append(f"{k}: {len(v)} variações")
        return '; '.join(parts) if parts else 'Nenhum detectado'

    def generate_platform_variations(self, structure, output_dir):
        """Generate ready-to-paste prompt files for each vibe-code platform."""
        self.log("🎯 Gerando variações para plataformas de vibe-code...")
        var_dir = os.path.join(output_dir, '_variações')
        os.makedirs(var_dir, exist_ok=True)

        title = self.ds.get('title', 'Design System')
        css_block = self._build_css_block()
        colors = self._build_colors_summary()
        fonts = self._build_fonts_summary()
        comps = self._build_components_summary()
        html_files = structure.get('html', [])
        css_files = structure.get('css', [])

        # --- LOVABLE / BASE44 / CORE0 ---
        lovable = f"""# PROMPT DE IMPLEMENTAÇÃO — {title}
# Plataforma: Lovable / Base44 / Core0
# Cole este prompt inteiro no chat da plataforma.

Implemente o design system abaixo no meu projeto. Siga EXATAMENTE as cores, fontes e variáveis CSS.

## Design System Variables (CSS)
Crie um arquivo `design-system-variables.css` com este conteúdo e importe-o no arquivo principal:

```css
{css_block}
```

## Paleta de Cores
Cores principais: {colors}

## Tipografia
Fontes: {fonts}

## Componentes Detectados
{comps}

## Instruções de Implementação
1. Importe o CSS acima no `index.css` ou equivalente usando `@import './design-system-variables.css';`
2. Substitua todas as cores hardcoded pelas variáveis `var(--ds-color-N)`
3. Substitua fontes por `var(--ds-font-N)`
4. Mantenha a responsividade existente
5. NÃO remova funcionalidades — apenas aplique o visual do design system

## Arquivos do Projeto para Adaptar
{chr(10).join('- ' + f for f in html_files[:20])}
{chr(10).join('- ' + f for f in css_files[:20])}
"""
        with open(os.path.join(var_dir, 'prompt-lovable.md'), 'w', encoding='utf-8') as f:
            f.write(lovable)

        # --- CLAUDE CODE / ANTIGRAVITY ---
        claude = f"""# PROMPT DE IMPLEMENTAÇÃO — {title}
# Plataforma: Claude Code / Antigravity / Cursor
# Cole este prompt inteiro no terminal do agente.

Aplique o design system extraído abaixo no projeto atual. Siga as instruções passo a passo.

## Passo 1: Criar arquivo de variáveis
Crie o arquivo `src/design-system-variables.css` (ou na raiz se não houver `src/`):

```css
{css_block}
```

## Passo 2: Importar no projeto
Adicione `@import './design-system-variables.css';` no topo do arquivo CSS principal do projeto.

## Passo 3: Aplicar variáveis
Nos seguintes arquivos, substitua:
- Cores hexadecimais → `var(--ds-color-N)` correspondente
- Font-family → `var(--ds-font-N)` correspondente

Arquivos alvo:
{chr(10).join('- `' + f + '`' for f in css_files[:15])}
{chr(10).join('- `' + f + '`' for f in html_files[:15])}

## Passo 4: Componentes
{comps}

## Regras
- Não quebre funcionalidades existentes
- Mantenha a estrutura de pastas
- Aplique as variáveis de forma consistente em TODOS os arquivos
- Faça commit após cada arquivo modificado
"""
        with open(os.path.join(var_dir, 'prompt-claude-code.md'), 'w', encoding='utf-8') as f:
            f.write(claude)

        # --- GOOGLE AI STUDIO ---
        studio = f"""# PROMPT DE IMPLEMENTAÇÃO — {title}
# Plataforma: Google AI Studio / Gemini
# Cole este prompt no chat do AI Studio com o código do projeto anexado.

Analise o projeto anexado e aplique o seguinte design system em todos os arquivos de estilo e componentes.

## CSS Variables para Aplicar
```css
{css_block}
```

## Cores: {colors}
## Fontes: {fonts}
## Componentes: {comps}

Retorne APENAS os arquivos modificados com o código completo atualizado, prontos para substituir os originais.
Não inclua explicações — apenas código.
"""
        with open(os.path.join(var_dir, 'prompt-google-studio.md'), 'w', encoding='utf-8') as f:
            f.write(studio)

        # --- JSON Universal (para qualquer integração programática) ---
        universal = {
            'platform': 'universal',
            'design_system': title,
            'css_variables': css_block,
            'colors': self.ds.get('colors', [])[:15],
            'fonts': self.ds.get('fonts', [])[:5],
            'components': {k: len(v) for k, v in self.ds.get('components', {}).items()},
            'target_files': {
                'html': html_files[:30],
                'css': css_files[:30],
            }
        }
        with open(os.path.join(var_dir, 'integration-data.json'), 'w', encoding='utf-8') as f:
            json.dump(universal, f, indent=2, ensure_ascii=False)

        self.log("✅ 4 variações geradas: Lovable, Claude Code, Google Studio, Universal JSON")
        return ['prompt-lovable.md', 'prompt-claude-code.md', 'prompt-google-studio.md', 'integration-data.json']

    def create_adaptation_package(self, output_dir):
        """Create the full adaptation package (Prompt Hub Mode)."""
        self.log("📦 Criando pacote de adaptação (Prompt Hub)...")
        os.makedirs(output_dir, exist_ok=True)

        # We analyze the project but DO NOT copy its files to the output.
        # This keeps the output clean and focused on AI Prompts.
        structure = self.analyze_project()

        # 1. Generate CSS Tokens
        css_vars = self.generate_css_variables()
        with open(os.path.join(output_dir, 'design-system-variables.css'), 'w', encoding='utf-8') as f:
            f.write(css_vars)

        # 2. Generate Guide & AI Plan
        guide = self.generate_adaptation_guide(structure)
        ai_plan = self.generate_ai_adaptation_plan(structure)
        with open(os.path.join(output_dir, 'adaptation-guide.md'), 'w', encoding='utf-8') as f:
            f.write(guide)
            if ai_plan:
                f.write("\n\n---\n\n# Plano de Adaptação Inteligente (AI)\n\n")
                f.write(ai_plan)

        with open(os.path.join(output_dir, 'design-system-data.json'), 'w', encoding='utf-8') as f:
            json.dump(self.ds, f, indent=2, ensure_ascii=False)

        # 3. Generate platform-specific variations
        variations = self.generate_platform_variations(structure, output_dir)
        
        # 4. Generate the Prompt Hub index.html
        self._generate_prompt_hub_html(output_dir)

        self.log(f"✅ Pacote Prompt Hub gerado com sucesso ({len(variations)} variações).")
        return output_dir

    def _generate_prompt_hub_html(self, output_dir):
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Onyx Prompt Hub ⚡</title>
    <style>
        :root {{
            --bg: #0a0a0a;
            --surface: #141414;
            --border: #222;
            --primary: #8a2be2;
            --primary-hover: #9d4edd;
            --text: #e0e0e0;
            --text-muted: #888;
        }}
        body {{
            background: var(--bg); color: var(--text); font-family: 'Inter', system-ui, sans-serif;
            margin: 0; padding: 2rem; line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ margin-bottom: 3rem; text-align: center; }}
        h1 {{ color: #fff; font-size: 2.5rem; margin-bottom: 0.5rem; letter-spacing: -0.02em; }}
        h1 span {{ color: var(--primary); }}
        .subtitle {{ color: var(--text-muted); font-size: 1.1rem; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .card {{
            background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
            padding: 1.5rem; transition: transform 0.2s, border-color 0.2s;
            display: flex; flex-direction: column;
        }}
        .card:hover {{ transform: translateY(-2px); border-color: var(--primary); }}
        .card h2 {{ margin: 0 0 0.5rem 0; font-size: 1.25rem; color: #fff; }}
        .card p {{ margin: 0 0 1.5rem 0; color: var(--text-muted); font-size: 0.95rem; flex-grow: 1; }}
        
        .btn {{
            display: inline-flex; align-items: center; justify-content: center;
            background: var(--primary); color: #fff; text-decoration: none;
            padding: 0.75rem 1rem; border-radius: 8px; font-weight: 500;
            transition: background 0.2s; border: none; cursor: pointer; width: 100%; box-sizing: border-box;
        }}
        .btn:hover {{ background: var(--primary-hover); }}
        .btn-outline {{ background: transparent; border: 1px solid var(--border); color: var(--text); }}
        .btn-outline:hover {{ border-color: var(--primary); background: rgba(138, 43, 226, 0.1); }}
        
        .sys-info {{ margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border); font-size: 0.85rem; color: var(--text-muted); text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Onyx <span>Prompt Hub</span></h1>
            <div class="subtitle">Seus assets de IA foram compilados. O projeto original não foi modificado.</div>
        </header>

        <div class="grid">
            <div class="card">
                <h2>🎨 Design System CSS</h2>
                <p>Todos os tokens extraídos (cores, fontes, animações) em variáveis CSS prontas para uso.</p>
                <a href="design-system-variables.css" target="_blank" class="btn btn-outline">Abrir Variáveis CSS</a>
            </div>

            <div class="card">
                <h2>🤖 Prompt Lovable / Cursor</h2>
                <p>Mega-prompt otimizado para IAs de geração de código autônoma e context-aware.</p>
                <a href="_variações/prompt-lovable.md" target="_blank" class="btn">Abrir Prompt Lovable</a>
            </div>

            <div class="card">
                <h2>💬 Prompt Claude / ChatGPT</h2>
                <p>Guia passo-a-passo detalhado para IAs conversacionais adaptarem a estrutura do seu projeto.</p>
                <a href="_variações/prompt-claude-code.md" target="_blank" class="btn">Abrir Prompt Claude</a>
            </div>
            
            <div class="card">
                <h2>📄 Guia de Adaptação Geral</h2>
                <p>O plano arquitetural completo mapeando o design system para a estrutura do seu projeto.</p>
                <a href="adaptation-guide.md" target="_blank" class="btn btn-outline">Abrir Guia Master</a>
            </div>
        </div>
        
        <div class="sys-info">
            Gerado por Gravit Design Factory. Salve a pasta _variações para consultar os dados integrais.
        </div>
    </div>
</body>
</html>"""
        with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)



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
