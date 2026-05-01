"""
Gravit Design Factory — Design System Extractor
Analyzes captured HTML/CSS and generates a design-system.html file
following the Asimov Extract HTML Design System v2 prompt pattern.
"""

import re
import os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests


class DesignSystemExtractor:
    """Extracts typography, colors, components, layout, motion, and icons from HTML."""

    def __init__(self, html_content, base_url='', assets_dir=''):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = base_url
        self.assets_dir = assets_dir
        self.data = {
            'typography': [],
            'colors': [],
            'surfaces': [],
            'gradients': [],
            'components': {'buttons': [], 'cards': [], 'inputs': [], 'pills': [], 'navs': []},
            'layout': [],
            'motion': {'keyframes': [], 'transitions': [], 'hover': []},
            'icons': [],
            'hero_html': '',
            'css_links': [],
            'js_links': [],
            'fonts': [],
            'title': '',
        }

    def extract_all(self):
        """Run full extraction pipeline."""
        self._extract_meta()
        self._extract_assets()
        self._extract_hero()
        self._extract_typography()
        self._extract_colors()
        self._extract_components()
        self._extract_layout()
        self._extract_motion()
        self._extract_icons()
        self._refine_with_ai()
        return self.data

    def _extract_meta(self):
        title_tag = self.soup.find('title')
        self.data['title'] = title_tag.get_text(strip=True) if title_tag else 'Untitled'

    def _extract_assets(self):
        for link in self.soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                self.data['css_links'].append(href)
        for script in self.soup.find_all('script', src=True):
            self.data['js_links'].append(script['src'])
        for link in self.soup.find_all('link', rel='preconnect'):
            href = link.get('href', '')
            if 'fonts' in href:
                self.data['fonts'].append(href)

    def _extract_hero(self):
        hero = None
        for sel in ['section:first-of-type', '[class*="hero"]', 'header + section', 'main > section:first-child']:
            hero = self.soup.select_one(sel)
            if hero:
                break
        if not hero:
            body = self.soup.find('body')
            if body:
                sections = body.find_all('section', limit=1)
                hero = sections[0] if sections else None
        self.data['hero_html'] = str(hero) if hero else ''

    def _extract_typography(self):
        type_map = {}
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'li', 'label']:
            for el in self.soup.find_all(tag, limit=3):
                classes = ' '.join(el.get('class', []))
                key = f"{tag}.{classes}" if classes else tag
                if key not in type_map:
                    text = el.get_text(strip=True)[:80]
                    if text and len(text) > 2:
                        type_map[key] = {
                            'tag': tag,
                            'classes': classes,
                            'sample_text': text,
                            'html': str(el),
                        }
        self.data['typography'] = list(type_map.values())

    def _extract_colors(self):
        color_re = re.compile(r'(#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|hsla?\([^)]+\))')
        colors_found = set()
        for el in self.soup.find_all(attrs={'style': True}):
            style = el['style']
            for match in color_re.findall(style):
                colors_found.add(match)
        for el in self.soup.find_all(attrs={'class': True}):
            classes = el.get('class', [])
            for cls in classes:
                if any(k in cls for k in ['bg-', 'text-', 'border-', 'from-', 'to-', 'via-']):
                    colors_found.add(f"tw:{cls}")
        for style_tag in self.soup.find_all('style'):
            if style_tag.string:
                for match in color_re.findall(style_tag.string):
                    colors_found.add(match)
                gradient_re = re.compile(r'(linear-gradient\([^;]+\)|radial-gradient\([^;]+\))')
                for gm in gradient_re.findall(style_tag.string):
                    self.data['gradients'].append(gm)
        self.data['colors'] = list(colors_found)[:30]
        glass = self.soup.find_all(class_=lambda c: c and ('backdrop' in str(c) or 'glass' in str(c) or 'blur' in str(c)))
        for el in glass:
            self.data['surfaces'].append({
                'classes': ' '.join(el.get('class', [])),
                'html': str(el)[:500],
            })

    def _extract_components(self):
        for btn in self.soup.find_all('button', limit=10):
            self.data['components']['buttons'].append({
                'classes': ' '.join(btn.get('class', [])),
                'text': btn.get_text(strip=True)[:50],
                'html': str(btn),
            })
        for a in self.soup.find_all('a', limit=5):
            classes = ' '.join(a.get('class', []))
            if any(k in classes for k in ['btn', 'button', 'cta', 'rounded-full']):
                self.data['components']['buttons'].append({
                    'classes': classes,
                    'text': a.get_text(strip=True)[:50],
                    'html': str(a),
                })
        card_selectors = ['[class*="card"]', '[class*="rounded-2xl"]', '[class*="rounded-3xl"]']
        for sel in card_selectors:
            for card in self.soup.select(sel)[:5]:
                self.data['components']['cards'].append({
                    'classes': ' '.join(card.get('class', [])),
                    'html': str(card)[:1000],
                })
        for inp in self.soup.find_all(['input', 'textarea', 'select'], limit=5):
            self.data['components']['inputs'].append({
                'type': inp.get('type', 'text'),
                'classes': ' '.join(inp.get('class', [])),
                'html': str(inp),
            })
        pill_classes = ['pill', 'badge', 'tag', 'chip']
        for el in self.soup.find_all(class_=lambda c: c and any(k in str(c).lower() for k in pill_classes)):
            self.data['components']['pills'].append({
                'classes': ' '.join(el.get('class', [])),
                'text': el.get_text(strip=True)[:30],
                'html': str(el),
            })

    def _extract_layout(self):
        grid_classes = ['grid', 'flex', 'container', 'max-w-', 'mx-auto', 'col-span']
        for el in self.soup.find_all(class_=lambda c: c and any(k in str(c) for k in grid_classes), limit=10):
            classes = ' '.join(el.get('class', []))
            if len(classes) > 5:
                self.data['layout'].append({
                    'tag': el.name,
                    'classes': classes,
                })

    def _extract_motion(self):
        for style_tag in self.soup.find_all('style'):
            if style_tag.string:
                kf_re = re.compile(r'@keyframes\s+(\w+)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', re.DOTALL)
                for name, body in kf_re.findall(style_tag.string):
                    self.data['motion']['keyframes'].append({'name': name, 'body': body.strip()[:300]})
                trans_re = re.compile(r'transition[^;]*;')
                for t in trans_re.findall(style_tag.string):
                    self.data['motion']['transitions'].append(t.strip())
        hover_els = self.soup.find_all(class_=lambda c: c and any(k in str(c) for k in ['hover:', 'hover-', 'transition']))
        for el in hover_els[:10]:
            self.data['motion']['hover'].append(' '.join(el.get('class', [])))

    def _extract_icons(self):
        for svg in self.soup.find_all('svg', limit=20):
            icon_data = svg.get('data-icon', '')
            aria = svg.get('aria-label', '') or svg.get('aria-hidden', '')
            w = svg.get('width', svg.get('data-width', ''))
            h = svg.get('height', svg.get('data-height', ''))
            self.data['icons'].append({
                'icon': icon_data,
                'width': w,
                'height': h,
                'html': str(svg)[:800],
            })

    def _refine_with_ai(self):
        """Use Groq to refine the extracted data (niche, style, suggestions)."""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return

        model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        
        # Simple prompt to categorize based on extracted text
        text_sample = self.soup.get_text()[:2000]
        prompt = f"""Analyze this website text and provide a JSON with:
1. niche (one of: saas-ai, dashboard, portfolio, medical, automotive, ecommerce, landing, social, general)
2. style (comma separated: glass, dark, light, parallax, animation, gradient, minimal, modern)
3. primary_fonts (list of font names)
4. color_palette (list of hex codes)

Website Text:
{text_sample}

Return ONLY valid JSON."""

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                ai_data = res.json()['choices'][0]['message']['content']
                parsed = json.loads(ai_data)
                self.data['niche'] = parsed.get('niche', self.data.get('niche', 'general'))
                self.data['style'] = parsed.get('style', self.data.get('style', 'modern'))
                if parsed.get('primary_fonts'):
                    self.data['fonts'].extend(parsed['primary_fonts'])
                    self.data['fonts'] = list(set(self.data['fonts']))
                if parsed.get('color_palette'):
                    self.data['colors'].extend(parsed['color_palette'])
                    self.data['colors'] = list(set(self.data['colors']))
        except Exception as e:
            print(f"Groq Refinement Error: {e}")

    def to_json(self):
        return json.dumps(self.data, indent=2, ensure_ascii=False)


def extract_metadata_from_html(html_content):
    """Quick metadata extraction for cataloging."""
    soup = BeautifulSoup(html_content, 'html.parser')
    title = ''
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)

    fonts = set()
    for link in soup.find_all('link', href=True):
        if 'fonts' in link['href']:
            fonts.add(link['href'])
    for style in soup.find_all('style'):
        if style.string:
            for m in re.findall(r"font-family:\s*['\"]?([^;'\"]+)", style.string):
                fonts.add(m.strip().split(',')[0].strip())

    color_re = re.compile(r'#[0-9a-fA-F]{3,8}')
    colors = set()
    for style in soup.find_all('style'):
        if style.string:
            colors.update(color_re.findall(style.string))
    for el in soup.find_all(attrs={'style': True}):
        colors.update(color_re.findall(el['style']))

    body = soup.find('body')
    body_classes = ' '.join(body.get('class', [])) if body else ''

    niche = _guess_niche(title, soup.get_text()[:2000])
    style = _guess_style(body_classes, soup)

    return {
        'title': title,
        'fonts': list(fonts)[:5],
        'colors': list(colors)[:10],
        'niche': niche,
        'style': style,
    }


def _guess_niche(title, text):
    """Heuristic niche classification."""
    t = (title + ' ' + text).lower()
    if any(k in t for k in ['ai', 'automation', 'machine learning', 'neural', 'gpt']):
        return 'saas-ai'
    if any(k in t for k in ['dashboard', 'analytics', 'metrics', 'monitor']):
        return 'dashboard'
    if any(k in t for k in ['portfolio', 'photographer', 'gallery', 'creative']):
        return 'portfolio'
    if any(k in t for k in ['medical', 'health', 'clinic', 'doctor']):
        return 'medical'
    if any(k in t for k in ['ev', 'electric', 'automotive', 'car']):
        return 'automotive'
    if any(k in t for k in ['shop', 'store', 'marketplace', 'ecommerce', 'price', 'buy']):
        return 'ecommerce'
    if any(k in t for k in ['captura', 'landing', 'hero', 'launch', 'waitlist']):
        return 'landing'
    if any(k in t for k in ['social', 'instagram', 'tiktok', 'youtube']):
        return 'social'
    return 'general'


def _guess_style(body_classes, soup):
    """Heuristic style classification."""
    all_classes = body_classes
    for el in soup.find_all(class_=True, limit=50):
        all_classes += ' ' + ' '.join(el.get('class', []))
    ac = all_classes.lower()
    styles = []
    if any(k in ac for k in ['glass', 'backdrop', 'blur', 'frosted']):
        styles.append('glass')
    if any(k in ac for k in ['bg-neutral-950', 'bg-black', 'bg-gray-900', 'dark']):
        styles.append('dark')
    if any(k in ac for k in ['bg-white', 'bg-gray-50', 'light']):
        styles.append('light')
    if any(k in ac for k in ['parallax', 'scroll-', 'translate']):
        styles.append('parallax')
    if any(k in ac for k in ['animate', 'animation', 'motion', 'keyframe']):
        styles.append('animation')
    if any(k in ac for k in ['gradient', 'from-', 'to-', 'via-']):
        styles.append('gradient')
    if any(k in ac for k in ['min-h-screen', 'minimal', 'clean']):
        styles.append('minimal')
    return ','.join(styles) if styles else 'modern'
