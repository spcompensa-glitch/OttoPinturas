"""
import_with_dedup.py — Importação Apify com anti-duplicata e filtro de qualidade.

Fluxo:
1. Conecta ao PostgreSQL e busca todos os nomes de leads existentes
2. Roda o Apify Google Maps Extractor (5 regiões × 3 categorias)
3. Filtra: só importa leads NOVOS com telefone OU email
4. Salva no PostgreSQL e mostra resultados
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.database import Database
from src.utils.apify_client import (
    ApifyClient,
    import_all_regions,
    REGIONS_FOCAL,
    SEARCH_CONFIGS,
)
from src.utils.logger import logger

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN", "")


def get_existing_names(db) -> set:
    """Busca todos os nomes de leads existentes no PostgreSQL."""
    names = set()
    try:
        with db._get_connection() as conn:
            cur = db._run_query(conn, "SELECT LOWER(TRIM(name)) FROM leads")
            rows = cur.fetchall() if hasattr(cur, 'fetchall') else conn.execute("SELECT LOWER(TRIM(name)) FROM leads").fetchall()
            for row in rows:
                name = row[0] if isinstance(row, tuple) else row
                if name:
                    names.add(name.strip())
    except Exception as e:
        logger.warning(f"Erro ao buscar nomes existentes: {e}")

    logger.info(f"Encontrados {len(names)} nomes existentes no banco")
    return names


def main():
    print("=" * 60)
    print("  IMPORTAÇÃO APIFY COM ANTI-DUPLICATA")
    print("=" * 60)

    if not APIFY_TOKEN:
        print("ERRO: APIFY_API_TOKEN não configurado no .env")
        return

    # 1. Conectar ao banco
    print("\n[1/4] Conectando ao PostgreSQL...")
    db = Database()
    if not db.is_postgres:
        print("ERRO: Não conectou ao PostgreSQL")
        return
    print(f"  Conectado: PostgreSQL")

    # 2. Buscar nomes existentes
    print("\n[2/4] Buscando nomes existentes no banco...")
    existing_names = get_existing_names(db)
    print(f"  {len(existing_names)} nomes já existem")

    # 3. Configurar importação
    print("\n[3/4] Configurando importação...")
    print(f"  Regiões: {len(REGIONS_FOCAL)} (focal)")
    for r in REGIONS_FOCAL:
        print(f"    - {r['name']}")
    print(f"  Categorias: {len(SEARCH_CONFIGS)}")
    for k, v in SEARCH_CONFIGS.items():
        print(f"    - {k}: '{v['search']}'")
    print(f"  Max por busca: 100")
    print(f"  Email enrichment: HABILITADO")
    print(f"  Anti-duplicata: HABILITADO")
    print(f"  Filtro qualidade: phone OU email obrigatório")

    total_buscas = len(REGIONS_FOCAL) * len(SEARCH_CONFIGS)
    print(f"\n  Total de buscas: {total_buscas}")
    print(f"  Custo estimado: ~$3-5 (plano Free)")

    # 4. Executar importação
    print("\n[4/4] Executando importação...")
    print("-" * 60)

    def progresso(atual, total, novos, acumulado):
        pct = (atual / total) * 100
        print(f"  [{atual}/{total}] {pct:.0f}% — {novos} novos nesta busca — Total: {acumulado}")

    resultado = import_all_regions(
        token=APIFY_TOKEN,
        db=db,
        max_per_category=100,
        regions=REGIONS_FOCAL,
        categories=SEARCH_CONFIGS,
        existing_names=existing_names,
        progress_callback=progresso,
    )

    # 5. Resultados
    print("\n" + "=" * 60)
    print("  RESULTADO FINAL")
    print("=" * 60)
    print(f"  Leads novos importados:  {resultado['imported']}")
    print(f"  Pulados (duplicados):    {resultado['skipped_dup']}")
    print(f"  Pulados (sem contato):   {resultado['skipped_no_contact']}")
    print(f"  Erros:                   {resultado['skipped_error']}")
    print(f"  Total processado:        {resultado['total']}")

    # 6. Verificar banco depois da importação
    print("\n[VERIFICAÇÃO] Consultando banco após importação...")
    try:
        with db._get_connection() as conn:
            cur = db._run_query(conn, "SELECT COUNT(*) FROM leads")
            row = cur.fetchone() if hasattr(cur, 'fetchall') else conn.execute("SELECT COUNT(*) FROM leads").fetchall()
            total = row[0] if isinstance(row, tuple) else row[0]
            print(f"  Total de leads no banco: {total}")

            cur2 = db._run_query(conn, "SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL AND phone != 'N/D' AND phone != ''")
            row2 = cur2.fetchone() if hasattr(cur2, 'fetchall') else conn.execute("SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL AND phone != 'N/D' AND phone != ''").fetchall()
            com_telefone = row2[0] if isinstance(row2, tuple) else row2[0]
            print(f"  Com telefone:            {com_telefone}")

            cur3 = db._run_query(conn, "SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != 'N/D' AND email != ''")
            row3 = cur3.fetchone() if hasattr(cur3, 'fetchall') else conn.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL AND email != 'N/D' AND email != ''").fetchall()
            com_email = row3[0] if isinstance(row3, tuple) else row3[0]
            print(f"  Com email:               {com_email}")
    except Exception as e:
        print(f"  Erro na verificação: {e}")

    print("\nImportação concluída!")


if __name__ == "__main__":
    main()
