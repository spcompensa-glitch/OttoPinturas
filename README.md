# Prospect-On 3.0 (Versão Atualizada)

Sistema automatizado de prospecção, captação e gestão de Leads focado no setor de Manutenção e Pintura Predial (Otto Pinturas).

## 🚀 O que há de novo na versão atual?
- **Integração Apify 2.0:** Atualização no mapeamento do robô de raspagem (Google Maps Scraper) para capturar perfeitamente os telefones e e-mails que antes estavam sendo perdidos.
- **Filtro Anti-Concorrentes:** O sistema agora bloqueia automaticamente a importação de "Empresas de Pintura Predial", buscando exclusivamente Síndicos, Administradoras de Condomínios e Empresas de Facilities de Grande Porte.
- **Expansão de Regiões:** O robô varre 11 regiões estratégicas (Zonas Sul, Leste, Norte, Oeste, Centro, Guarulhos, Campinas, SBC, Santo André, Osasco, Barueri).
- **Banco de Dados Restaurado:** A base original de contatos foi limpa, restaurada e deduplicada para manter a máxima qualidade dos dados (garantindo número de WhatsApp válido).
- **PostgreSQL (Railway):** Produção roda em PostgreSQL gerenciado; desenvolvimento local usa SQLite — fallback automático.
- **Sistema Multi-Agente:** 14 agentes autônomos orquestrados pelo ManagerAgent para descoberta, enriquecimento, qualificação e fechamento.
- **3 Pilares de Demanda:** A (Condomínios/GetNinjas), B (Grandes Obras/oHub), C (Editais Públicos/PNCP).
- **CRM por Lead + Chat:** Interações, favoritos exclusivos por vendedor, notas CRM (admin↔vendedor), mensagens não lidas.
- **Landing Page Pública:** Hero 3D, Portfolio, Partners, Simulador interativo de fachadas.

## 🏗 Arquitetura do Sistema

### 1. Frontend (Interface)
- **Tecnologia:** Next.js 16 (React 19) com TypeScript.
- **Estilização:** Tailwind CSS 3.4 + Framer Motion + Lucide Icons.
- **Porta Padrão:** `http://localhost:3000`
- **Principais Funcionalidades:**
  - Landing Page pública (Otto Pinturas) — Hero, Services, Portfolio, Partners, Neighborhood Simulator
  - Sistema autenticado (`/dashboard`, `/leads-quentes`, `/usuarios`, `/documentos`, `/minha-conta`)
  - Dashboard com métricas, filtros hierárquicos (Zona → Bairro), status comercial
  - Tabela de Leads com edição em massa, paginação, cards mobile
  - Modal de Detalhes/CRM: anotações, retorno, status, correção de fachada, chat em tempo real
  - Painel de Disparos WhatsApp (Evolution API)
  - Health Monitor, Usage Stats, Configurações, Histórico de Buscas

### 2. Backend (Servidor & Robôs)
- **Tecnologia:** Python 3.11+ (FastAPI).
- **Banco de Dados:** PostgreSQL (Railway) via `DATABASE_URL` — fallback automático para SQLite (`backend/data/prospecton.db`).
- **Porta Padrão:** `http://localhost:8002`
- **Automações Internas:**
  - `apify_client.py`: Comunicação com API da Apify (Google Maps Scraper) — 11 regiões × 3 categorias.
  - `database.py`: Motor de inserção/atualização (Upsert) com isolamento multi-usuário (`leads_quentes` com PK composta `id+user_id`).
  - **WhatsApp:** Integração com *Evolution API* para automação de mensagens diretas e em massa.
  - **IA:** DeepSeek Chat para qualificação semântica, extração de contatos, scoring.
  - **Vision:** Google Street View + Satellite + Gemini Vision para análise de fachadas.

### 3. Motor Multi-Agente (ManagerAgent v10.5)
Orquestra 14 agentes especializados:
| Agente | Responsabilidade |
|--------|------------------|
| `BrowserScoutAgent` | Google Maps via Playwright Stealth (sem Places API) |
| `DemandScoutAgent` | Varredura 3 Pilares: GetNinjas (A), oHub (B), PNCP/DOE (C) |
| `WebEnrichmentAgent` | Detetive web: busca contatos, sites, e-mails via Google Search stealth |
| `SemanticExtractorAgent` | DeepSeek: extrai CNPJ, síndico, administradora, intenção de obra |
| `LeadEnrichmentAgent` | DeepSeek: enriquece lead com valuation, ROI, proposta comercial |
| `ContactMiner` | Garimpa administradoras e síndicos profissionais |
| `HunterAgent` | OSM/Overpass (terciário, gratuito) |
| `SurveyorAgent` | Dados cadastrais, metragem, unidades |
| `ContactAgent` | Validação de telefones/WhatsApp |
| `ClosingAgent` | Geração de proposta, follow-up |
| `AnalystAgent` | Análise de mercado, preço m², saúde financeira |
| `GeosampaAgent` | Dados geoespaciais SP (zoneamento, vias) |
| `ExtensionLauncherAgent` | Abre browser com extensão Sniper carregada |
| `HealthAgent` | MonitoraAgent` | Monitora status de todas as APIs/serviços |

**Pipeline Sniper Demand-First (4 Fases):**
1. **Captação de Sinais** — DemandScoutAgent (Bing + DeepSeek)
2. **Mapeamento Cadastral** — BrowserScoutAgent (Google Maps Playwright Stealth)
3. **Detetive de Decisores** — SemanticExtractorAgent (CNPJ + Síndico/Administradora)
4. **Sniper de Contatos** — WebEnrichmentAgent (Contatos Validados)

## ⚙️ Como rodar o sistema localmente

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- PostgreSQL (opcional — usa SQLite por padrão)
- Conta Apify (para importação em massa)
- Conta Evolution API (para WhatsApp)
- Chave DeepSeek API

### Iniciar o Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
# Configure .env (ver abaixo)
python -m uvicorn api:app --host 0.0.0.0 --port 8002 --reload
```

### Iniciar o Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Variáveis de Ambiente Necessárias (`.env` no diretório `backend`)

```env
# Banco de Dados (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:vcTQXSwguUytTuistPUMBbjFbICuEipt@sakura.proxy.rlwy.net:27713/railway

# Apify (Google Maps Scraper)
APIFY_API_TOKEN=seu_token_apify

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://sua-instancia.evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_INSTANCE_NAME=otto_pinturas

# DeepSeek (Qualificação IA)
DEEPSEEK_API_KEY=sua_chave_deepseek

# Google Maps / Vision (opcional - para Street View/Satellite)
GOOGLE_MAPS_API_KEY=sua_chave_google_maps
GEMINI_API_KEY=sua_chave_gemini
```

> **Nota:** O sistema detecta automaticamente `DATABASE_URL`. Se válida (PostgreSQL), usa ela; senão cai para SQLite local (`data/prospecton.db`). `psycopg2-binary` já está no `requirements.txt`.

## 📡 Principais Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/leads` | Lista leads (isolado por usuário via header `X-User-Id`) |
| `GET` | `/api/leads-quentes` | Lista favoritos do usuário logado |
| `POST` | `/api/leads/{id}/favorite` | Marca/desmarca favorito (bloqueia se outro vendedor já reservou) |
| `POST` | `/api/leads/{id}/interaction` | Salva anotações, retorno, status, imagem de fachada |
| `GET` | `/api/leads/{id}/messages` | Chat do lead (marca como lido) |
| `POST` | `/api/leads/{id}/messages` | Envia mensagem no chat |
| `POST` | `/api/scan/start` | Dispara varredura Sniper completa |
| `POST` | `/api/scan-pillars` | Varredura 3 Pilares (A/B/C) paralela |
| `POST` | `/api/apify/import` | Importa leads Apify (todas regiões, background) |
| `GET` | `/api/contacts/search` | Garimpa administradoras/síndicos |
| `GET` | `/api/health` / `/api/system/health` | Healthcheck simples / detalhado |
| `GET` | `/api/usage` | Consumo de IA (DeepSeek, Apify, etc) |
| `GET/POST` | `/api/configuracoes` | Configurações do sistema (persistido em JSON) |
| `GET/POST/DELETE` | `/api/documents` | CRUD de documentos (admin only) |
| `WS` | `/ws/logs` | Logs em tempo real para o AgentConsole |

## 🗄️ Esquema do Banco de Dados

### `users`
- `id`, `email`, `password`, `name`, `role` (admin/vendedor), `phone`, `document`, `created_at`

### `leads` (tabela principal)
- `id` (PK), `name`, `address`, `lat`, `lng`, `score`, `justification`, `category`
- `responsavel_nome`, `responsavel_contato`, `phone`, `email`, `website`
- `vision_image_path`, `vision_image_url`, `satellite_image_path`
- `vision_analysis_json`, `market_json`, `valuation_json`, `financial_health_json`, `demand_json`
- `source`, `urgency_score`, `is_confirmed`, `contact_status`, `is_favorite`
- `interaction_notes`, `return_date`, `email_sent_at`
- `intencao_ativa`, `resumo_sinal`, `link_fonte`, `score_urgencia`, `categoria_demanda`, `pilar`
- `crm_notes`, `crm_response`, `created_at`, `updated_at`

### `leads_quentes` (tabela blindada — isolamento por vendedor)
- **PK Composta:** `(id, user_id)` — um lead pode ser favorito de múltiplos vendedores independentemente
- `user_id` (FK → users.id, ON DELETE CASCADE)
- Todos os campos de `leads` + `is_favorite DEFAULT TRUE`
- Garante exclusividade: vendedor não consegue favoritar lead já reservado por outro

### `search_history`
- `id`, `user_id`, `user_name`, `user_email`, `city`, `pilares`, `total_leads`, `leads_a`, `leads_b`, `leads_c`, `leads_json`, `searched_at`

### `lead_messages`
- `id`, `lead_id`, `user_id`, `user_name`, `message`, `created_at`, `is_read`
- Admin vê todas; vendedor vê apenas de seus favoritos

### `usage_stats`
- `service`, `calls_today`, `total_calls`, `last_used`

## 🌐 Deploy (Railway)

1. **Backend Service:** Root Directory = `/backend`
   - `DATABASE_URL` (PostgreSQL Railway) — **obrigatório**
   - `APIFY_API_TOKEN`, `EVOLUTION_*`, `DEEPSEEK_API_KEY`
   - Start Command: `python -m uvicorn api:app --host 0.0.0.0 --port $PORT`

2. **Frontend Service:** Root Directory = `/frontend`
   - `NEXT_PUBLIC_API_URL=https://seu-backend.railway.app`
   - Build Command: `npm run build`
   - Start Command: `npm start`

3. **PostgreSQL:** Railway provisiona automaticamente; a URL vai para `DATABASE_URL` do backend.

## 📁 Estrutura de Pastas

```
Prospect-On 3.0/
├── backend/
│   ├── api.py                 # FastAPI app (1113 linhas)
│   ├── main.py                # Script standalone de enriquecimento
│   ├── requirements.txt
│   ├── data/
│   │   └── prospecton.db      # SQLite fallback
│   ├── static/
│   │   ├── vistorias/         # Imagens de fachada/satélite
│   │   └── documentos/        # PDFs uploadados
│   └── src/
│       ├── agents/            # 14 agentes especializados
│       ├── crawler/           # Google Maps Playwright
│       ├── enrichment/        # CNPJ, ReceitaWS
│       ├── engine/            # ROI, Scoring, Pricing
│       ├── scraper/           # Market data, portais
│       └── utils/             # DB, Apify, Vision, Logger, Webhook, Reports
├── frontend/
│   ├── app/
│   │   ├── (landing)/         # Landing page Otto Pinturas
│   │   ├── (system)/          # Sistema autenticado
│   │   │   ├── dashboard/
│   │   │   ├── leads-quentes/
│   │   │   ├── usuarios/
│   │   │   ├── documentos/
│   │   │   └── minha-conta/
│   │   ├── api/               # API routes Next.js (proxy se necessário)
│   │   ├── components/        # Componentes compartilhados
│   │   ├── lib/               # api.ts, config.ts, data.ts
│   │   └── condo/[slug]/      # Página pública do condomínio
│   ├── public/AquivosOtto/    # Assets estáticos (portfolio, logos, docs)
│   ├── package.json
│   └── tailwind.config.ts
└── README.md
```

## 🧪 Testes e Scripts Úteis (Backend)

```bash
# Verificar conexão DB e contagem
cd backend && python check_db.py

# Limpar banco (cuidado!)
python -c "from src.utils.database import Database; Database().clear_all_leads()"

# Importar mock de 5 leads para teste
python inject_mock_5_leads.py

# Testar Apify (precisa token)
python run_apify_import.py

# Testar varredura Pilares
python test_pillars.py

# Verificar saúde das APIs
python -c "from src.agents.health_agent import HealthAgent; print(HealthAgent().get_system_health())"
```

---

*Documentação atualizada em Julho de 2026 — Reflete 100% o código em produção (PostgreSQL Railway, Multi-Agente, 3 Pilares, CRM/Chat, Landing Page).*