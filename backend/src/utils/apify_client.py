"""
ApifyClient — Integração com Apify para importação de leads.

Usa o Google Maps Extractor (compass) da Apify para buscar:
  - Administradoras de condomínios
  - Síndicos profissionais
  - Empresas de facilities/manutenção predial

Cada lead importado vem com: nome, telefone, email, endereço, site, coordenadas.
Filtros: anti-duplicata (verifica nomes existentes no DB) e qualidade (phone OU email obrigatório).
"""
import os
import re
import json
import time
import datetime
import requests
from src.utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")
APIFY_BASE = "https://api.apify.com/v2"

GOOGLE_MAPS_ACTOR = "compass~crawler-google-places"

SEARCH_CONFIGS = {
    "administradoras": {
        "search": "administradora de condominios",
        "category": "sindico_administradora",
    },
    "sindicos": {
        "search": "sindico profissional condominio",
        "category": "sindico_administradora",
    },
    "facilities": {
        "search": "facilities manutencao predial empresa",
        "category": "grande_porte",
    },
}

REGIONS = [
    {"name": "Sao Paulo — Zona Sul", "location": "Zona Sul, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Zona Norte", "location": "Zona Norte, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Zona Leste", "location": "Zona Leste, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Zona Oeste", "location": "Zona Oeste, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Centro", "location": "Centro, Sao Paulo, SP, Brasil"},
    {"name": "Guarulhos — SP", "location": "Guarulhos, SP, Brasil"},
    {"name": "Campinas — SP", "location": "Campinas, SP, Brasil"},
    {"name": "Sao Bernardo do Campo — SP", "location": "Sao Bernardo do Campo, SP, Brasil"},
    {"name": "Santo Andre — SP", "location": "Santo Andre, SP, Brasil"},
    {"name": "Osasco — SP", "location": "Osasco, SP, Brasil"},
    {"name": "Barueri — SP", "location": "Barueri, SP, Brasil"},
]

REGIONS_FOCAL = [
    {"name": "Sao Paulo — Centro", "location": "Centro, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Zona Sul", "location": "Zona Sul, Sao Paulo, SP, Brasil"},
    {"name": "Sao Paulo — Zona Oeste", "location": "Zona Oeste, Sao Paulo, SP, Brasil"},
    {"name": "Guarulhos — SP", "location": "Guarulhos, SP, Brasil"},
    {"name": "Campinas — SP", "location": "Campinas, SP, Brasil"},
]


class ApifyClient:
    """Cliente para interagir com a API da Apify."""

    def __init__(self, token: str = None):
        self.token = token or APIFY_TOKEN
        if not self.token:
            logger.warning("ApifyClient: APIFY_API_TOKEN não configurado no .env")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def run_google_maps_search(
        self,
        search: str,
        location: str = "Sao Paulo, SP, Brasil",
        max_results: int = 100,
        language: str = "pt-BR",
        include_emails: bool = True,
    ) -> list[dict]:
        """
        Executa o ator Google Maps Extractor e retorna os resultados.

        Args:
            search: Termo de busca (ex: "administradora de condominios")
            location: Localização (ex: "Sao Paulo, SP, Brasil")
            max_results: Máximo de resultados (padrão 100 para economizar $)
            language: Idioma (padrão pt-BR)
            include_emails: Habilitar email enrichment (padrão True)

        Returns:
            Lista de dicts com os leads encontrados
        """
        if not self.token:
            logger.error("ApifyClient: Token não configurado")
            return []

        logger.info(f"ApifyClient: Buscando '{search}' em '{location}' (max={max_results}, emails={include_emails})...")

        # Input do ator — compass~crawler-google-places (pago, mais dados)
        actor_input = {
            "searchStringsArray": [search],
            "locationQuery": location,
            "maxCrawledPlacesPerSearch": max_results,
            "language": language,
            "maxImages": 0,
            "maxReviews": 0,
            "includeOpeningHours": False,
            "includePopularTimes": False,
            "includeQuestionsAndAnswers": False,
            "includePeopleAlsoSearch": False,
            "debug": False,
        }

        try:
            # Inicia o ator
            run_url = f"{APIFY_BASE}/acts/{GOOGLE_MAPS_ACTOR}/runs"
            resp = requests.post(
                run_url,
                headers=self.headers,
                json=actor_input,
                timeout=30,
            )

            if resp.status_code != 201:
                logger.error(f"ApifyClient: Erro ao iniciar ator: {resp.status_code} {resp.text[:200]}")
                return []

            run_data = resp.json()
            run_id = run_data["data"]["id"]
            logger.info(f"ApifyClient: Ator iniciado, run_id={run_id}")

            # Aguarda a conclusão (polling)
            dataset_id = self._wait_for_completion(run_id)

            if not dataset_id:
                logger.error("ApifyClient: Ator não completou ou não gerou dataset")
                return []

            # Baixa os resultados
            results = self._fetch_dataset(dataset_id)
            logger.info(f"ApifyClient: {len(results)} resultados baixados para '{search}'")

            return results

        except Exception as e:
            logger.error(f"ApifyClient: Erro ao executar ator: {e}")
            return []

    def _wait_for_completion(self, run_id: str, timeout: int = 600) -> str | None:
        """Aguarda o ator terminar e retorna o dataset_id."""
        status_url = f"{APIFY_BASE}/acts/{GOOGLE_MAPS_ACTOR}/runs/{run_id}"
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                resp = requests.get(status_url, headers=self.headers, timeout=15)
                if resp.status_code != 200:
                    time.sleep(10)
                    continue

                data = resp.json()
                status = data.get("data", {}).get("status", "")
                
                logger.info(f"ApifyClient: Status={status}")

                if status in ("SUCCEEDED", "succeeded"):
                    default_dataset_id = data.get("data", {}).get("defaultDatasetId", "")
                    return default_dataset_id

                if status in ("FAILED", "TIMED-OUT", "ABORTED", "failed", "timed-out", "aborted"):
                    logger.error(f"ApifyClient: Ator finalizou com status {status}")
                    return None

                time.sleep(15)

            except Exception as e:
                logger.warning(f"ApifyClient: Erro no polling: {e}")
                time.sleep(15)

        logger.error(f"ApifyClient: Timeout aguardando conclusao do ator")
        return None

    def _fetch_dataset(self, dataset_id: str) -> list[dict]:
        """Baixa todos os itens do dataset."""
        items_url = f"{APIFY_BASE}/datasets/{dataset_id}/items?format=json&clean=true"
        all_items = []

        try:
            resp = requests.get(items_url, headers=self.headers, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    all_items = data
                elif isinstance(data, dict) and "items" in data:
                    all_items = data["items"]
                else:
                    all_items = [data] if data else []
        except Exception as e:
            logger.error(f"ApifyClient: Erro ao baixar dataset: {e}")

        return all_items

    def normalize_lead(self, raw: dict, category: str = "", region: str = "") -> dict | None:
        """
        Normaliza um lead bruto da Apify para o formato interno.
        Retorna None se o lead não tiver telefone OU email válido.
        """
        name = raw.get("title", "")
        if not name:
            return None

        # Telefone
        phone = raw.get("phoneUnformatted") or raw.get("phone", "")
        if not phone:
            phones = raw.get("phones", [])
            if phones:
                phone = phones[0].get("phoneUnformatted") or phones[0].get("phone", "")

        # Email
        email = raw.get("email", "")
        if not email:
            emails = raw.get("emails", [])
            if emails:
                email = emails[0]

        # Filtro de qualidade: precisa ter phone válido
        has_phone = phone and phone.strip() not in ("", "N/D", "None")
        has_email = email and email.strip() not in ("", "N/D", "None")
        if not has_phone:
            return None

        # Endereço
        address = raw.get("address", "")
        if not address:
            street = raw.get("street", "")
            city = raw.get("city", "")
            state = raw.get("state", "")
            postal = raw.get("postalCode", "")
            address = f"{street}, {city} - {state}, {postal}".strip(", -")

        # Website
        website = raw.get("website", "") or raw.get("companyUrl", "")

        # Coordenadas
        coords = None
        loc = raw.get("location", {})
        if loc and loc.get("lat") and loc.get("lng"):
            coords = {"lat": loc["lat"], "lng": loc["lng"]}

        # Score baseado nos dados disponíveis
        score = 5.0
        if has_phone and has_email:
            score = 9.0
        elif has_phone or has_email:
            score = 7.0
        if website:
            score += 0.5
        if address:
            score += 0.5

        now = datetime.datetime.now().isoformat()

        return {
            "name": name.strip(),
            "address": address.strip() if address else (region or "Sao Paulo, SP"),
            "phone": phone.strip() if has_phone else "N/D",
            "email": email.strip() if has_email else "N/D",
            "website": website.strip() if website else "N/D",
            "lat": coords["lat"] if coords else None,
            "lng": coords["lng"] if coords else None,
            "score": min(score, 10.0),
            "category": category or "lead_apify",
            "source": f"Apify — {region or 'SP'}",
            "justification": f"Lead importado via Apify Google Maps Extractor — {category} — {region}",
            "urgency_score": 7.0,
            "contact_status": "Aguardando Abordagem",
            "pilar": "M",
            "created_at": now,
            "updated_at": now,
        }


def get_import_stats() -> dict:
    """Retorna estatísticas sobre a importação: regiões, categorias e total estimado."""
    total_regions = len(REGIONS)
    total_categories = len(SEARCH_CONFIGS)
    total_estimated = total_regions * total_categories * 200
    return {
        "regions": total_regions,
        "categories": total_categories,
        "estimated_leads": total_estimated,
        "regions_list": [r["name"] for r in REGIONS],
        "categories_list": list(SEARCH_CONFIGS.keys()),
    }


def import_all_regions(
    token: str,
    db=None,
    max_per_category: int = 100,
    regions: list = None,
    categories: dict = None,
    existing_names: set = None,
    progress_callback=None,
) -> dict:
    """
    Importa leads de todas as regiões e categorias.

    Args:
        token: Apify API token
        db: Instância do Database (opcional — salva direto no DB)
        max_per_category: Máximo de leads por busca (padrão 100)
        regions: Lista de regiões (padrão: REGIONS_FOCAL)
        categories: Dict de categorias (padrão: SEARCH_CONFIGS)
        existing_names: Set de nomes já existentes no DB (anti-duplicata)
        progress_callback: Função de callback para progresso

    Returns:
        {"imported": int, "skipped_dup": int, "skipped_no_contact": int, "total": int}
    """
    client = ApifyClient(token=token)
    all_leads = []
    total_imported = 0
    total_skipped_dup = 0
    total_skipped_no_contact = 0
    total_skipped_error = 0
    seen_names = set(existing_names) if existing_names else set()
    regions_to_use = regions or REGIONS_FOCAL
    cats_to_use = categories or SEARCH_CONFIGS

    total_buscas = len(regions_to_use) * len(cats_to_use)
    busca_atual = 0

    for region in regions_to_use:
        region_name = region["name"]
        logger.info(f"ApifyClient: Importando região {region_name}...")

        for cat_key, config in cats_to_use.items():
            busca_atual += 1
            logger.info(f"ApifyClient:   [{busca_atual}/{total_buscas}] Categoria '{cat_key}' em '{region_name}'")

            raw_results = client.run_google_maps_search(
                search=config["search"],
                location=region["location"],
                max_results=max_per_category,
                include_emails=True,
            )

            region_new = 0
            region_dup = 0
            region_no_contact = 0

            for raw in raw_results:
                normalized = client.normalize_lead(
                    raw,
                    category=config["category"],
                    region=region_name,
                )

                if not normalized:
                    region_no_contact += 1
                    total_skipped_no_contact += 1
                    continue

                # Anti-duplicata: verificar se nome já existe no DB
                key = normalized["name"].lower().strip()
                if key in seen_names:
                    region_dup += 1
                    total_skipped_dup += 1
                    continue

                seen_names.add(key)
                all_leads.append(normalized)

                if db:
                    try:
                        db.upsert_lead(normalized)
                        total_imported += 1
                        region_new += 1
                    except Exception as e:
                        logger.warning(f"ApifyClient: Erro ao salvar: {e}")
                        total_skipped_error += 1
                else:
                    total_imported += 1
                    region_new += 1

            logger.info(f"ApifyClient:     Resultado: {region_new} novos, {region_dup} duplicados, {region_no_contact} sem contato")

            if progress_callback:
                progress_callback(busca_atual, total_buscas, region_new, total_imported)

            time.sleep(2)

    logger.info(
        f"ApifyClient: Importação concluída — {total_imported} novos, "
        f"{total_skipped_dup} duplicados, {total_skipped_no_contact} sem contato, "
        f"{total_skipped_error} erros"
    )

    return {
        "imported": total_imported,
        "skipped_dup": total_skipped_dup,
        "skipped_no_contact": total_skipped_no_contact,
        "skipped_error": total_skipped_error,
        "total": total_imported + total_skipped_dup + total_skipped_no_contact + total_skipped_error,
    }
