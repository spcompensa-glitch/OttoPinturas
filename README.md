# Prospect-On 3.0 (Versão Atualizada)

Sistema automatizado de prospecção, captação e gestão de Leads focado no setor de Manutenção e Pintura Predial (Otto Pinturas).

## 🚀 O que há de novo na versão atual?
- **Integração Apify 2.0:** Atualização no mapeamento do robô de raspagem (Google Maps Scraper) para capturar perfeitamente os telefones e e-mails que antes estavam sendo perdidos.
- **Filtro Anti-Concorrentes:** O sistema agora bloqueia automaticamente a importação de "Empresas de Pintura Predial", buscando exclusivamente Síndicos, Administradoras de Condomínios e Empresas de Facilities de Grande Porte.
- **Expansão de Regiões:** O robô varre 11 regiões estratégicas (Zonas Sul, Leste, Norte, Oeste, Centro, Guarulhos, Campinas, SBC, Santo André, Osasco, Barueri).
- **Banco de Dados Restaurado:** A base original de contatos foi limpa, restaurada e deduplicada para manter a máxima qualidade dos dados (garantindo número de WhatsApp válido).

## 🏗 Arquitetura do Sistema

O projeto é dividido em dois blocos principais:

### 1. Frontend (Interface)
- **Tecnologia:** Next.js (React) com TypeScript.
- **Estilização:** Tailwind CSS (Design System atualizado).
- **Porta Padrão:** `http://localhost:3000`
- **Principais Funcionalidades:** Dashboard de controle, Tabela de Leads com edição em massa, Integração visual do mapa de leads, e Painel de Disparos de WhatsApp.

### 2. Backend (Servidor & Robôs)
- **Tecnologia:** Python (FastAPI).
- **Banco de Dados:** SQLite (`backend/data/prospecton.db`) com tabelas isoladas para leads, leads_quentes, usuários e histórico.
- **Porta Padrão:** `http://localhost:8002`
- **Automações Internas:**
  - `apify_client.py`: Módulo responsável pela comunicação com a API da Apify.
  - `database.py`: Motor de inserção e atualização (Upsert) que garante que leads repetidos apenas atualizem seus dados sem duplicar.
  - **WhatsApp:** Integração com a *Evolution API* para automação de mensagens diretas e em massa.

## ⚙️ Como rodar o sistema localmente

### Iniciar o Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api:app --host 0.0.0.0 --port 8002 --reload
```

### Iniciar o Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Variáveis de Ambiente Necessárias (`.env`)
No diretório `backend`, você precisará do arquivo `.env` configurado com:
- `APIFY_API_TOKEN` (Para a raspagem de dados)
- Chaves do WhatsApp (Evolution API)
- `DEEPSEEK_API_KEY` (Para qualificação inteligente de dados)

---
*Documentação atualizada em Julho de 2026 durante a revisão de estabilidade e banco de dados.*
