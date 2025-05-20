import sqlite3

conn = sqlite3.connect("laudos.db")
cursor = conn.cursor()

# Adiciona a coluna "responsavel" se ainda não existir
try:
    cursor.execute("ALTER TABLE fardos ADD COLUMN responsavel TEXT")
    print("Coluna 'responsavel' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    print("A coluna já existe ou houve outro erro:", e)

conn.commit()
conn.close()