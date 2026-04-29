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
- index.html

