# PROMPT DE IMPLEMENTAÇÃO — Mira.ai - Intelligence Engine
# Plataforma: Lovable / Base44 / Core0
# Cole este prompt inteiro no chat da plataforma.

Implemente o design system abaixo no meu projeto. Siga EXATAMENTE as cores, fontes e variáveis CSS.

## Design System Variables (CSS)
Crie um arquivo `design-system-variables.css` com este conteúdo e importe-o no arquivo principal:

```css
:root {
  --ds-color-1: #e5e5e5;
  --ds-color-2: #050505;
  --ds-color-3: #fff;
  --ds-font-1: "Geist", sans-serif;
  --ds-font-2: "Playfair Display", sans-serif;
  --ds-font-3: "Space Grotesk", sans-serif;
}

```

## Paleta de Cores
Cores principais: #e5e5e5, #050505, #fff

## Tipografia
Fontes: Geist, Playfair Display, Space Grotesk

## Componentes Detectados
Nenhum detectado

## Instruções de Implementação
1. Importe o CSS acima no `index.css` ou equivalente usando `@import './design-system-variables.css';`
2. Substitua todas as cores hardcoded pelas variáveis `var(--ds-color-N)`
3. Substitua fontes por `var(--ds-font-N)`
4. Mantenha a responsividade existente
5. NÃO remova funcionalidades — apenas aplique o visual do design system

## Arquivos do Projeto para Adaptar
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\canvas-visual.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\canvas-visual.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\digital-architect.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\digital-architect.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\flux-motion.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\flux-motion.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\fluxora.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\fluxora.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\futureui.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\futureui.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\genlabs.aura.build\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\genlabs.aura.build\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\glass-effect2\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\glass-effect2\index.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\glass-effect2\assets\filter_3E_3Crect_width__100_25_ef7da59166f5.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\glass-green-effect\design-system.html
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_0b2072b66163.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_0fc20595ebff.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_19fd9cc6b396.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_23afcbef9bdd.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_2b2d87bc82d8.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_4fef849c83da.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_62759cd015bd.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_6f16cdd6fd9f.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_70fd47a02eed.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_82ced711bf49.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_86e10c4bcbd4.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_8e191ef32247.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_94cb6f0c406a.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_9b8bf743d4a8.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_a7b22b336fe1.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_b52fc18295f8.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_f495c2faa2a6.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_fa22aa91016e.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\assets\css2_19fd9cc6b396.css
- Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\assets\css2_a7b22b336fe1.css
