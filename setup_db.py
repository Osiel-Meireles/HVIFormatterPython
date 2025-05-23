import sqlite3

DB_NAME = "laudos.db"

def recriar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Deleta tabelas existentes, se houver
    cursor.execute("DROP TABLE IF EXISTS fardos")
    cursor.execute("DROP TABLE IF EXISTS formatacoes")
    cursor.execute("DROP TABLE IF EXISTS usuarios")

    # Cria tabela de usuários
    cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha_hash TEXT,
        tipo TEXT,
        regiao TEXT,
        senha_temporaria INTEGER
    )
    """)

    # Cria tabela de formatações com campo 'responsavel'
    cursor.execute("""
    CREATE TABLE formatacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote TEXT,
        data_formatacao TEXT,
        data_hvi TEXT,
        safra TEXT,
        produtor TEXT,
        usuario_id INTEGER,
        responsavel TEXT
    )
    """)

    # Cria tabela de fardos - Corrigida para corresponder ao que é usado em services/database.py
    cursor.execute("""
    CREATE TABLE fardos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        formatacao_id INTEGER,
        fardo_id TEXT,
        mic REAL,
        uhml REAL,
        str REAL,
        sfi REAL,
        ui REAL,
        csp REAL,
        elg REAL,
        rd REAL,
        b REAL,
        trid TEXT,
        sci REAL,
        mat REAL,
        cg TEXT,
        produtor TEXT,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados recriado com sucesso!")

if __name__ == "__main__":
    recriar_banco()
