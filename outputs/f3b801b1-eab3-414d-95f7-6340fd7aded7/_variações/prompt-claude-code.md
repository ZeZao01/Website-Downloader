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

- `index.html`

## Passo 4: Componentes
Nenhum detectado

## Regras
- Não quebre funcionalidades existentes
- Mantenha a estrutura de pastas
- Aplique as variáveis de forma consistente em TODOS os arquivos
- Faça commit após cada arquivo modificado
