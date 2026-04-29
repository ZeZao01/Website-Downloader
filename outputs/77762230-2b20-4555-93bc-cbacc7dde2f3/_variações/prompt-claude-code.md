# PROMPT DE IMPLEMENTAÇÃO — Mira.ai - Intelligence Engine
# Plataforma: Claude Code / Antigravity / Cursor
# Cole este prompt inteiro no terminal do agente.

Aplique o design system extraído abaixo no projeto atual. Siga as instruções passo a passo.

## Passo 1: Criar arquivo de variáveis
Crie o arquivo `src/design-system-variables.css` (ou na raiz se não houver `src/`):

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

## Passo 2: Importar no projeto
Adicione `@import './design-system-variables.css';` no topo do arquivo CSS principal do projeto.

## Passo 3: Aplicar variáveis
Nos seguintes arquivos, substitua:
- Cores hexadecimais → `var(--ds-color-N)` correspondente
- Font-family → `var(--ds-font-N)` correspondente

Arquivos alvo:
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_0b2072b66163.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_0fc20595ebff.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_19fd9cc6b396.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_23afcbef9bdd.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_2b2d87bc82d8.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_4fef849c83da.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_62759cd015bd.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_6f16cdd6fd9f.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_70fd47a02eed.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_82ced711bf49.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_86e10c4bcbd4.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_8e191ef32247.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_94cb6f0c406a.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_9b8bf743d4a8.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\assets\css2_a7b22b336fe1.css`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-automation-17.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\ai-social-automation.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\canvas-visual.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\canvas-visual.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\digital-architect.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\digital-architect.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\flux-motion.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\flux-motion.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\fluxora.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\fluxora.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\futureui.aura.build\design-system.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\futureui.aura.build\index.html`
- `Website-Downloader-main\Formação AI Designer - Asimov\design systems\genlabs.aura.build\design-system.html`

## Passo 4: Componentes
Nenhum detectado

## Regras
- Não quebre funcionalidades existentes
- Mantenha a estrutura de pastas
- Aplique as variáveis de forma consistente em TODOS os arquivos
- Faça commit após cada arquivo modificado
