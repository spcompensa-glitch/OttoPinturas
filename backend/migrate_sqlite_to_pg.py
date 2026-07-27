import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor

def migrate():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Erro: DATABASE_URL nao encontrada no ambiente.")
        return

    sqlite_path = "data/prospecton.db"
    if not os.path.exists(sqlite_path):
        print(f"Erro: Banco SQLite não encontrado em {sqlite_path}")
        return

    print("Conectando ao PostgreSQL...")
    try:
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        qs = dict(urllib.parse.parse_qsl(parsed.query))
        if 'sslmode' not in qs:
            qs['sslmode'] = 'disable'
        qs['connect_timeout'] = '10'
        new_query = urllib.parse.urlencode(qs)
        pg_url = urllib.parse.urlunparse(parsed._replace(query=new_query))
        pg_conn = psycopg2.connect(pg_url)
        pg_cur = pg_conn.cursor()
    except Exception as e:
        print(f"Erro ao conectar no Postgres: {e}")
        return

    print("Conectando ao SQLite...")
    sl_conn = sqlite3.connect(sqlite_path)
    sl_conn.row_factory = sqlite3.Row
    sl_cur = sl_conn.cursor()

    tables = ["users", "leads", "leads_quentes", "search_history", "lead_messages"]

    for table in tables:
        try:
            sl_cur.execute(f"SELECT * FROM {table}")
            rows = sl_cur.fetchall()
            if not rows:
                print(f"Tabela {table} vazia no SQLite.")
                continue
                
            print(f"Migrando {len(rows)} linhas da tabela {table}...")
            
            # Pega as colunas da primeira linha
            cols = list(rows[0].keys())
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            
            for row in rows:
                values = [row[c] for c in cols]
                # Se for tabela com ID, tentar inserir ou ignorar se ja existir
                if table == "users":
                    # ON CONFLICT DO NOTHING para users baseado no email
                    query = f"""
                        INSERT INTO {table} ({col_names}) 
                        VALUES ({placeholders}) 
                        ON CONFLICT (email) DO NOTHING
                    """
                elif table == "leads":
                    query = f"""
                        INSERT INTO {table} ({col_names}) 
                        VALUES ({placeholders}) 
                        ON CONFLICT (id) DO NOTHING
                    """
                elif table == "leads_quentes":
                    query = f"""
                        INSERT INTO {table} ({col_names}) 
                        VALUES ({placeholders}) 
                        ON CONFLICT (id, user_id) DO NOTHING
                    """
                else:
                    # Para tabelas sem pk customizada definida explicitamente no conflito (search_history id é SERIAL mas pode colidir)
                    # Melhor deletar tudo antes ou ignorar erro? Vamos ignorar erro de ID.
                    query = f"""
                        INSERT INTO {table} ({col_names}) 
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING
                    """
                try:
                    pg_cur.execute(query, values)
                except Exception as ex:
                    # Pode acontecer erro de PK em history, a gente ignora e faz rollback na transacao local
                    pg_conn.rollback()
                    pass
            pg_conn.commit()
            print(f"[{table}] OK")
        except Exception as te:
            print(f"Erro ao migrar {table}: {te}")
            pg_conn.rollback()

    print("=== MIGRACAO CONCLUIDA ===")
    pg_conn.close()
    sl_conn.close()

if __name__ == "__main__":
    migrate()
