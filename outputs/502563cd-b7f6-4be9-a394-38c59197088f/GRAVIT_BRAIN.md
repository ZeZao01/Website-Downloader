# 🧠 GRAVIT DIGITAL BRAIN — RESUME PROTOCOL

Este arquivo serve como memória forçada para o agente Antigravity e para o sistema. Ele deve ser lido em cada nova sessão para garantir continuidade absoluta.

## 📍 Estado Atual (Checkpoint)
- **Fase:** Migração Supabase Concluída / Deploy Pendente.
- **Data:** 2026-04-27
- **Progresso:** 4 etapas do pipeline integradas com SupabaseDB.
- **Sessão Ativa:** Recuperação automática de projetos implementada no `index` route.

## 🔑 Credenciais (Configuradas no .env)
- **Supabase:** Conectado via Service Role (mbqnjjtgiiowadtltkwi).
- **IA Extraction:** Groq (Llama 3.3 70b).
- **IA Adaptation:** OpenRouter (Claude 3.5 Sonnet).

## 🛠️ Pendências Técnicas
1. **Sincronização:** O usuário precisa rodar `catalog_existing.py` após rodar o SQL de correção das colunas (`colors`, `fonts`, `has_design_system`).
2. **Deploy:** Preparar `render.yaml` e `Procfile` para Render.com.
3. **Persistência UI:** O front-end (`index.html`) precisa ser atualizado para reagir ao `active_project` enviado pelo Flask.

## 📂 Estrutura de Storage (Buckets Criados)
- `model-previews`: Imagens de capa.
- `model-zips`: Arquivos fonte dos modelos.
- `project-uploads`: Projetos reais enviados pelo usuário.
- `adaptation-outputs`: Resultados da etapa 4.

## 🚀 Próximo Passo Imediato
- Criar arquivos de Deploy (`render.yaml`, `build.sh`).
- Atualizar a UI para mostrar o projeto recuperado.

---
**Protocolo Wilk: Continuidade Garantida.**
