import sqlite3

def clean_competitors():
    db_path = 'C:/Users/spcom/Desktop/OttoPinturas1.0/Prospect-On 3.0/backend/data/prospecton.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM leads WHERE category = 'pintura_predial' OR justification LIKE '%pintura predial%'")
    deleted = c.rowcount
    conn.commit()
    conn.close()
    print(f"Deletados {deleted} concorrentes (empresas de pintura predial).")

if __name__ == "__main__":
    clean_competitors()
