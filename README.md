# Prospect-On 3.0

Sistema automatizado de prospecção, captação e gestão de Leads focado no setor de Manutenção e Pintura Predial (Otto Pinturas).

## O que há de novo na versão atual?

- **PostgreSQL (Railway):** Produção roda em PostgreSQL gerenciado com `sslmode=require`; desenvolvimento local usa SQLite — fallback automático.
- **Integração Apify 2.0:** Google Maps Scraper captura telefones e e-mails com normalização por fornecedor (G Maps Extractor, Outscraper, etc).
- **Filtro Anti-Concorrentes:** Bloqueia automaticamente empresas de pintura predial, buscando exclusivamente síndicos, administradoras e empresas de facilities.
- **Expansão de Regiões:** 11 regiões estratégicas (Zonas Sul, Leste, Norte, Oeste, Centro, Guarulhos, Campinas, SBC, Santo André, Osasco, Barueri).
- **Sistema Multi-Agente:** 16 agentes autônomos orquestrados pelo ManagerAgent v10.0.
- **3 Pilares de Demanda:** A (Condomínios/GetNinjas), B (Grandes Obras/oHub), C (Editais Públicos/PNCP).
- **CRM por Lead + Chat:** Interações, favoritos exclusivos por vendedor, notas CRM (admin↔vendedor), mensagens não lidas, fixar/Atribuir lead.
- **Gestão de Documentos:** Upload/download/delete de PDFs e planilhas (admin only).
- **Landing Page Pública:** Hero 3D (Spline), Portfolio, Partners, Simulador interativo de fachadas.

## Arquitetura do Sistema

### 1. Frontend (Interface)

- **Framework:** Next.js 16.2.1 (React 19.2.4) + TypeScript 5.9.3
- **Estilização:** Tailwind CSS 3.4.17 + Framer Motion 12.0.0
- **Ícones:** Lucide React 0.469.0
- **Mapas:** Leaflet 1.9.4 + React Leaflet 4.2.1
- **PDF:** jsPDF 2.5.2 + html2canvas 1.4.1
- **Validação:** Zod 3.25.67
- **Porta Padrão:** `http://localhost:3000`

**Componentes do Sistema (10):**

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
| `AgentConsole` | `AgentConsole.tsx` | Console de logs em tempo real via WebSocket |
| `ChatPanel` | `ChatPanel.tsx` | Chat por lead com envio, exclusão e contagem de não lidos |
| `LeadDetailModal` | `LeadDetailModal.tsx` | Modal de detalhes/CRM: notas, retorno, status, fachada, chat |
| `LeadTable` | `LeadTable.tsx` | Tabela paginada com filtros (status, pilar, zona/bairro), cards mobile |
| `ReportViewer` | `ReportViewer.tsx` | Visualizador de relatórios com projeções financeiras e download PDF |
| `Sidebar` | `Sidebar.tsx` | Navegação lateral com badge de mensagens não lidas (polling 10s) |
| `StatCard` | `StatCard.tsx` | Card reutilizável de métricas com ícone, valor, tendência |
| `SystemHealth` | `SystemHealth.tsx` | Dashboard de saúde dos serviços (OSM, Maps, Gemini, BrasilAPI) |
| `UsageIndicator` | `UsageIndicator.tsx` | Indicador de consumo de IA (DeepSeek, Apify, etc) |
| `VistoriaManualModal` | `VistoriaManualModal.tsx` | Modal de vistoria manual (torres, andares, área m², urgência) |

**Componentes da Landing Page (9):**

| Componente | Descrição |
|------------|-----------|
| `HomeHeader` | Navbar com logo, formulário de login, hamburger mobile |
| `HomeHero` | Hero com viewport 3D Spline, CTAs, badges de confiança |
| `BuildingsBackground` | Silhuetas SVG animadas de prédios |
| `NeighborhoodInteractive` | Simulador de fachadas interativo (click-to-paint + confetti) |
| `HomeServices` | 4 cards de serviço: Condomínios, Fachadas, Galpões, Industriais |
| `HomePortfolio` | Galeria filtrável de 28+ projetos com busca e lightbox |
| `HomePartners` | Carrossel de 6 parceiros + 13 clientes |
| `HomePillars` | Pilar da Empresa: Missão, Visão, Valores, Compromisso |
| `HomeFooter` | Footer com contato, links e texto legal |

**Rotas/Páginas:**

| Rota | Descrição | Auth |
|------|-----------|------|
| `/` | Landing Page Otto Pinturas | Não |
| `/politica-privacidade` | Política de Privacidade (LGPD) | Não |
| `/termos-uso` | Termos de Uso | Não |
| `/condo/[slug]` | Página pública do condomínio | Não |
| `/dashboard` | Cockpit principal: tabela de leads, filtros, importação Apify | Sim |
| `/leads-quentes` | Leads favoritos (Elite) + criação manual de lead | Sim |
| `/usuarios` | Gerenciamento de vendedores | Admin |
| `/documentos` | Gestão de documentos (upload admin) | Sim |
| `/minha-conta` | Perfil do usuário (nome, email, telefone, senha) | Sim |

### 2. Backend (Servidor & Robôs)

- **Framework:** FastAPI (Python 3.11+; Railway usa 3.13)
- **Banco de Dados:** PostgreSQL (Railway) via `DATABASE_URL` — fallback automático para SQLite (`backend/data/prospecton.db`)
- **Porta Padrão:** `http://localhost:8002`
- **Dependências:** googlemaps, requests, python-dotenv, pandas, pytest, fpdf2, fastapi, uvicorn, python-multipart, pillow, google-genai, psycopg2-binary, redis, playwright, pydantic, httpx

**Integrações:**

| Serviço | Uso |
|---------|-----|
| DeepSeek API | Qualificação semântica, extração de contatos, scoring |
| Google Places API | Dados estruturados, fotos, detalhes de lugares |
| Google Gemini | Análise de fachadas (legado) |
| Google Maps / Playwright Stealth | Descoberta de leads sem custo de API |
| OpenStreetMap Overpass API | Descoberta terciária gratuita |
| BrasilAPI | Consulta de CNPJ |
| Apify | Scraping em massa do Google Maps (pago) |
| Evolution API | Mensagens WhatsApp (alertas de leads quentes) |
| DuckDuckGo | Descoberta de leads via busca |
| GetNinjas | Pilar A — cotações ativas de pintura |
| oHub | Pilar B — grandes obras e facilities |
| PNCP/DOE-SP | Pilar C — editais públicos governamentais |

### 3. Motor Multi-Agente (ManagerAgent v10.0)

Orquestra 16 agentes especializados:

| Agente | Responsabilidade |
|--------|------------------|
| `ManagerAgent` | Orquestrador mestre. Executa pipeline de 4 fases. Injeta WebSocket para logs em tempo real |
| `BrowserScoutAgent` | Google Maps via Playwright Stealth (sem Places API). User agents stealth, viewports, scripts anti-detecção |
| `DemandScoutAgent` | Varredura 3 Pilares (A/B/C) paralela via `asyncio.gather`. DuckDuckGo + DeepSeek |
| `PillarAHunterAgent` | Pilar A — Condomínios via GetNinjas (cotações ativas de pintura) |
| `PillarBHunterAgent` | Pilar B — Grandes Obras via oHub (shoppings, hospitais, industriais) |
| `PillarCHunterAgent` | Pilar C — Editais Públicos via PNCP/DOE-SP (estratégia híbrida DuckDuckGo + Playwright) |
| `WebEnrichmentAgent` | Detetive web: Google Search stealth para contatos, sites, e-mails |
| `SemanticExtractorAgent` | DeepSeek: extrai CNPJ, síndico, administradora, intenção de obra |
| `LeadEnrichmentAgent` | DeepSeek: enriquece lead com tipo de imóvel, sinais, scoring, canais |
| `ContactMiner` | Garimpa administradoras e síndicos: BrasilAPI, DuckDuckGo, Google Maps |
| `HunterAgent` | Terciário gratuito: OpenStreetMap Overpass API com bounding box |
| `SurveyorAgent` | Estimativa de torres, andares, área total m² (DeepSeek + fallback) |
| `ContactAgent` | Validação de CNPJ, administrador e síndico via BrasilAPI |
| `ClosingAgent` | Consolida dados e gera proposta PDF final via ReportGenerator |
| `AnalystAgent` | NLP com DeepSeek: contexto comercial, dados de mercado, condições |
| `GeosampaAgent` | Dados públicos SP: idade do prédio via Geosampa/IPTU |
| `HealthAgent` | Monitora saúde de todas as APIs (OSM, Maps, DeepSeek, Gemini, BrasilAPI) |
| `ExtensionLauncherAgent` | Abre Chromium com extensão Google Maps Scraper carregada |
| `DemandScraperAgent` | Monitora portais CoteiBem e SindicoNet para novas cotações |

**Pipeline Sniper Demand-First (4 Fases):**

1. **Captação de Sinais** — DemandScoutAgent (DuckDuckGo + DeepSeek)
2. **Mapeamento Cadastral** — BrowserScoutAgent (Google Maps Playwright Stealth)
3. **Detetive de Decisores** — SemanticExtractorAgent (CNPJ + Síndico/Administradora)
4. **Sniper de Contatos** — WebEnrichmentAgent (Contatos Validados via Google Search)

## Variáveis de Ambiente

`.env` no diretório `backend`:

```env
# Banco de Dados (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:senha@sakura.proxy.rlwy.net:porta/railway

# Apify (Google Maps Scraper)
APIFY_API_TOKEN=seu_token_apify

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://sua-instancia.evolution-api.com
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_INSTANCE_NAME=otto_pinturas

# DeepSeek (Qualificação IA)
DEEPSEEK_API_KEY=sua_chave_deepseek

# Google Maps / Vision
GOOGLE_MAPS_API_KEY=sua_chave_google_maps
GEMINI_API_KEY=sua_chave_gemini
```

> **Nota:** O sistema detecta automaticamente `DATABASE_URL`. Se válida (PostgreSQL), usa ela; senão cai para SQLite local (`data/prospecton.db`). `psycopg2-binary` já está no `requirements.txt`.

## Endpoints da API (44 rotas)

### Autenticação & Usuários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/auth/login` | Login (email/senha) |
| `GET` | `/api/users/profile` | Perfil do usuário logado |
| `PUT` | `/api/users/profile` | Atualizar perfil |
| `GET` | `/api/admin/users` | Listar todos os usuários (admin) |
| `POST` | `/api/admin/users` | Criar vendedor (admin) |
| `DELETE` | `/api/admin/users/{user_id}` | Deletar vendedor (admin) |
| `GET` | `/api/admin/users/{user_id}/leads-quentes` | Leads quentes de um vendedor (admin) |
| `GET` | `/api/admin/pending-responses` | Contagem de respostas CRM pendentes (admin) |

### Leads

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/leads` | Lista leads (isolado por usuário via `X-User-Id`) |
| `GET` | `/api/leads-quentes` | Lista favoritos do usuário logado |
| `GET` | `/api/leads/by-slug/{slug}` | Busca lead por slug (URL pública) |
| `DELETE` | `/api/leads/{lead_id}` | Deleta um lead |
| `POST` | `/api/leads/clear` | Limpa todos os leads |
| `POST` | `/api/leads/import` | Importação em bulk (normaliza de múltiplos fornecedores) |

### CRM & Interações

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/leads/{lead_id}/interaction` | Salva anotações, retorno, status, imagem de fachada |
| `POST` | `/api/leads/{lead_id}/favorite` | Alterna favorito (bloqueia se outro vendedor já reservou) |
| `POST` | `/api/leads/{lead_id}/crm` | Envia lead para CRM |
| `PUT` | `/api/leads/{lead_id}/crm-notes` | Salva notas CRM + resposta do admin |

### Chat

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/leads/{lead_id}/messages` | Mensagens do chat (marca como lido) |
| `POST` | `/api/leads/{lead_id}/messages` | Envia mensagem |
| `DELETE` | `/api/leads/{lead_id}/messages/{message_id}` | Deleta mensagem própria |
| `GET` | `/api/messages/unread` | Contagem de mensagens não lidas |

### Varredura & Scan

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/scan/start` | Dispara varredura Sniper completa |
| `POST` | `/api/sniper/start` | Alias para scan/start |
| `GET` | `/api/scan-pillars` | Varredura 3 Pilares (A/B/C) paralela |
| `POST` | `/api/scan/extension` | Abre browser com extensão |
| `POST` | `/api/apify/import` | Importa leads Apify (todas regiões, background) |
| `GET` | `/api/apify/stats` | Estatísticas de importação Apify |
| `GET` | `/api/contacts/search` | Garimpa administradoras/síndicos |
| `GET` | `/api/search-history` | Histórico de buscas (admin: todas, vendedor: próprias) |
| `DELETE` | `/api/search-history/{entry_id}` | Deleta entrada do histórico |

### Análise & IA

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/analyze-lead` | Análise completa (enriquecimento + relatório + sync DB) |

### Sistema & Config

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Healthcheck raiz |
| `GET` | `/api/health` | Healthcheck simples |
| `GET` | `/api/system/health` | Healthcheck detalhado (todos os serviços) |
| `GET` | `/api/usage` | Consumo de IA (DeepSeek, Apify, etc) |
| `GET/POST` | `/api/configuracoes` | Configurações do sistema (persistido em JSON) |
| `GET/POST/DELETE` | `/api/documents` | CRUD de documentos (upload admin only) |

### Relatórios & Imagens

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/reports/{filename}` | Download de relatório PDF |
| `GET` | `/api/images/{filename}` | Serve imagens (CORS bypass) |

### WebSocket

| Protocolo | Endpoint | Descrição |
|-----------|----------|-----------|
| `WS` | `/ws/logs` | Logs em tempo real para o AgentConsole |

## Esquema do Banco de Dados

### `users`

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `id` | SERIAL / INTEGER | PRIMARY KEY |
| `email` | VARCHAR(255) / TEXT | UNIQUE NOT NULL |
| `password` | VARCHAR(255) / TEXT | NOT NULL |
| `name` | VARCHAR(255) / TEXT | NOT NULL |
| `role` | VARCHAR(50) / TEXT | NOT NULL (admin/vendedor) |
| `phone` | VARCHAR(50) / TEXT | |
| `document` | VARCHAR(50) / TEXT | |
| `created_at` | VARCHAR(100) / TEXT | |

**Seed:** `joao.ottopinturas@gmail.com` (admin), `jonatasprojetos2013@gmail.com` (admin)

### `leads` (tabela principal — 37 colunas)

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `id` | TEXT | PRIMARY KEY (slug normalizado) |
| `name` | TEXT | NOT NULL |
| `address` | TEXT | |
| `lat` | REAL | |
| `lng` | REAL | |
| `score` | REAL | Score de Oportunidade Otto (0-10) |
| `justification` | TEXT | |
| `category` | TEXT | ex: "ALERTA VERMELHO (URGENTE)" |
| `responsavel_nome` | TEXT | |
| `responsavel_contato` | TEXT | |
| `vision_image_path` | TEXT | Caminho local |
| `vision_image_url` | TEXT | URL HTTP |
| `satellite_image_path` | TEXT | |
| `vision_analysis_json` | TEXT | JSON blob |
| `market_json` | TEXT | JSON blob |
| `valuation_json` | TEXT | JSON blob |
| `financial_health_json` | TEXT | JSON blob |
| `demand_json` | TEXT | JSON blob |
| `source` | TEXT | "Radar", "Apify", "Pilar X", etc |
| `urgency_score` | REAL | |
| `is_confirmed` | BOOLEAN | DEFAULT FALSE |
| `email` | TEXT | |
| `social_url` | TEXT | |
| `booking_url` | TEXT | |
| `scanned_at` | TEXT | |
| `enriched_at` | TEXT | |
| `interaction_notes` | TEXT | Notas CRM |
| `return_date` | TEXT | Data de retorno |
| `email_sent_at` | TEXT | |
| `is_favorite` | BOOLEAN | DEFAULT FALSE |
| `contact_status` | TEXT | DEFAULT 'Aguardando Abordagem' |
| `intencao_ativa` | BOOLEAN | DEFAULT FALSE |
| `resumo_sinal` | TEXT | Resumo do sinal detectado |
| `link_fonte` | TEXT | URL de origem |
| `score_urgencia` | INTEGER | DEFAULT 0 |
| `categoria_demanda` | TEXT | ex: "pintura_fachada", "lavagem_pastilhas" |
| `pilar` | TEXT | DEFAULT 'A' (A, B ou C) |
| `crm_notes` | TEXT | Notas do admin |
| `crm_response` | TEXT | Resposta do admin |
| `created_at` | TEXT | |
| `updated_at` | TEXT | |

### `leads_quentes` (isolamento por vendedor)

Mesmas colunas de `leads` + adicional:

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `user_id` | INTEGER | NOT NULL, FK → users.id ON DELETE CASCADE |
| `is_favorite` | BOOLEAN | DEFAULT TRUE |

**PK Composta:** `(id, user_id)` — um lead pode ser favorito de múltiplos vendedores independentemente.

Garante exclusividade: um vendedor não consegue favoritar lead já reservado por outro.

### `usage_stats`

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `service` | TEXT | PRIMARY KEY (ex: "deepseek", "apify", "places") |
| `calls_today` | INTEGER | DEFAULT 0 |
| `total_calls` | INTEGER | DEFAULT 0 |
| `last_used` | TEXT | Timestamp ISO |

### `search_history`

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `id` | SERIAL / INTEGER | PRIMARY KEY |
| `user_id` | INTEGER | NOT NULL, FK → users.id |
| `user_name` | VARCHAR(255) / TEXT | NOT NULL |
| `user_email` | VARCHAR(255) / TEXT | NOT NULL |
| `city` | VARCHAR(255) / TEXT | NOT NULL |
| `pilares` | VARCHAR(255) / TEXT | NOT NULL (ex: "A,B,C") |
| `total_leads` | INTEGER | NOT NULL |
| `leads_a` | INTEGER | DEFAULT 0 |
| `leads_b` | INTEGER | DEFAULT 0 |
| `leads_c` | INTEGER | DEFAULT 0 |
| `leads_json` | TEXT | JSON completo do resultado |
| `searched_at` | VARCHAR(100) / TEXT | NOT NULL |

### `lead_messages`

| Coluna | Tipo | Constraints |
|--------|------|-------------|
| `id` | SERIAL / INTEGER | PRIMARY KEY |
| `lead_id` | VARCHAR(255) / TEXT | NOT NULL |
| `user_id` | INTEGER | NOT NULL, FK → users.id |
| `user_name` | VARCHAR(255) / TEXT | NOT NULL |
| `message` | TEXT | NOT NULL |
| `created_at` | VARCHAR(100) / TEXT | NOT NULL |
| `is_read` | BOOLEAN | DEFAULT FALSE |

**Visibilidade:** Admin vê todas as mensagens. Vendedor vê apenas mensagens dos seus favoritos.

## Deploy (Railway)

1. **Backend Service:** Root Directory = `/backend`
   - `DATABASE_URL` (PostgreSQL Railway) — obrigatório
   - `APIFY_API_TOKEN`, `EVOLUTION_*`, `DEEPSEEK_API_KEY`, `GOOGLE_MAPS_API_KEY`
   - Start: `python -m uvicorn api:app --host 0.0.0.0 --port $PORT`

2. **Frontend Service:** Root Directory = `/frontend`
   - `NEXT_PUBLIC_API_URL=https://seu-backend.railway.app`
   - `BACKEND_URL=https://seu-backend.railway.app`
   - Build: `npm run build`
   - Start: `npm start`

3. **PostgreSQL:** Railway provisiona automaticamente; a URL vai para `DATABASE_URL` do backend.

## Estrutura de Pastas

```
Prospect-On 3.0/
├── backend/
│   ├── api.py                 # FastAPI app (44 rotas, 1113 linhas)
│   ├── main.py                # Script standalone de enriquecimento
│   ├── start.sh               # Script de produção (playwright install + uvicorn)
│   ├── requirements.txt       # 17 dependências Python
│   ├── data/
│   │   └── prospecton.db      # SQLite fallback
│   ├── static/
│   │   ├── vistorias/         # Imagens de fachada/satélite
│   │   └── documentos/        # PDFs uploadados
│   └── src/
│       ├── agents/            # 16 agentes especializados
│       ├── crawler/           # Google Maps Playwright
│       ├── enrichment/        # CNPJ (cnpj_ws.py)
│       ├── engine/            # Smart Enrichment, ROI, Scoring, Pricing
│       ├── scraper/           # Market data, portais
│       └── utils/             # DB, Apify, Vision, DeepSeek, Logger, Webhook, Reports, Places, CSV, Diagrams
├── frontend/
│   ├── app/
│   │   ├── (landing)/         # Landing page Otto Pinturas (9 componentes)
│   │   │   └── components/    # HomeHeader, HomeHero, HomePortfolio, etc
│   │   ├── (system)/          # Sistema autenticado
│   │   │   ├── dashboard/     # Cockpit principal
│   │   │   ├── leads-quentes/ # Favoritos (Elite)
│   │   │   ├── usuarios/      # Gerenciamento (admin)
│   │   │   ├── documentos/    # Gestão de documentos
│   │   │   └── minha-conta/   # Perfil do usuário
│   │   ├── api/               # API routes Next.js (proxy para backend)
│   │   ├── components/        # 10 componentes compartilhados
│   │   ├── lib/               # api.ts, config.ts
│   │   └── condo/[slug]/      # Página pública do condomínio
│   ├── public/AquivosOtto/    # Assets estáticos (portfolio, logos, parceiros)
│   ├── next.config.ts         # Config Next.js (rewrites proxy)
│   ├── tailwind.config.ts     # Config Tailwind (cores otto, animações)
│   ├── railway.json           # Config Railway (healthcheck, restart)
│   └── package.json           # v3.2.0, 18 dependências
└── README.md
```

## Como Rodar Localmente

### Pré-requisitos

- Python 3.11+ (produção usa 3.13)
- Node.js 20+
- PostgreSQL (opcional — usa SQLite por padrão)
- Conta Apify (para importação em massa)
- Conta Evolution API (para WhatsApp)
- Chave DeepSeek API

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
# Configure .env (ver Variáveis de Ambiente)
python -m uvicorn api:app --host 0.0.0.0 --port 8002 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

*Documentação atualizada em Julho de 2026 — Reflete 100% do código em produção.*
