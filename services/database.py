import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "laudos.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha_hash TEXT,
        tipo TEXT,
        regiao TEXT,
        senha_temporaria INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS formatacoes (
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fardos (
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

def inserir_formatacao(lote, data_hvi, safra, produtor, responsavel):
    conn = conectar()
    cursor = conn.cursor()
    data_formatacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO formatacoes (lote, data_formatacao, data_hvi, safra, produtor, responsavel)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (lote, data_formatacao, data_hvi, safra, produtor, responsavel))

    conn.commit()
    id_formatacao = cursor.lastrowid
    conn.close()
    return id_formatacao

def inserir_fardos(formatacao_id, df, usuario_nome):
    conn = conectar()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO fardos (
                formatacao_id, fardo_id, mic, uhml, str, sfi, ui, csp, elg,
                rd, b, trid, sci, mat, cg, produtor, tipo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            formatacao_id,
            row["FardoID"],
            float(row["MIC"]) if str(row["MIC"]).replace(".", "", 1).isdigit() else None,
            float(row["UHML"]) if str(row["UHML"]).replace(".", "", 1).isdigit() else None,
            float(row["STR"]) if str(row["STR"]).replace(".", "", 1).isdigit() else None,
            float(row["SFI"]) if str(row["SFI"]).replace(".", "", 1).isdigit() else None,
            float(row["UI"]) if str(row["UI"]).replace(".", "", 1).isdigit() else None,
            float(row["CSP"]) if str(row["CSP"]).replace(".", "", 1).isdigit() else None,
            float(row["ELG"]) if str(row["ELG"]).replace(".", "", 1).isdigit() else None,
            float(row["Rd"]) if str(row["Rd"]).replace(".", "", 1).isdigit() else None,
            float(row["+b"]) if str(row["+b"]).replace(".", "", 1).isdigit() else None,
            row["TrID"],
            float(row["SCI"]) if str(row["SCI"]).replace(".", "", 1).isdigit() else None,
            float(row["MAT"]) if str(row["MAT"]).replace(".", "", 1).isdigit() else None,
            row["CG"],
            row["Produtor"],
            row["Tipo"]
        ))

    conn.commit()
    conn.close()

def listar_formatacoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.lote, f.safra, f.produtor, f.data_hvi, f.data_formatacao, f.responsavel,
               COUNT(fa.id) as total_fardos
        FROM formatacoes f
        LEFT JOIN fardos fa ON f.id = fa.formatacao_id
        GROUP BY f.id
        ORDER BY f.id DESC
    """)
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def listar_fardos_por_formatacao(formatacao_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fardo_id, mic, uhml, str, sfi, ui, csp, elg,
               rd, b, trid, sci, mat, cg, produtor, tipo
        FROM fardos
        WHERE formatacao_id = ?
    """, (formatacao_id,))
    colunas = [
        "FardoID", "MIC", "UHML", "STR", "SFI", "UI", "CSP", "ELG",
        "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=colunas)

def consultar_registros_completos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.lote, fa.fardo_id, fa.mic, fa.uhml, fa.str, fa.sfi, fa.ui, fa.csp, fa.elg,
               fa.rd, fa.b, fa.trid, fa.sci, fa.mat, fa.cg, fa.produtor, fa.tipo
        FROM fardos fa
        JOIN formatacoes f ON fa.formatacao_id = f.id
    """)
    colunas = [
        "Lote", "FardoID", "MIC", "UHML", "STR", "SFI", "UI", "CSP", "ELG",
        "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo"
    ]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=colunas)
