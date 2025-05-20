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
        INSERT INTO formatacoes (lote, data_formatacao, data_hvi, safra, produtor, usuario_id, responsavel)
        VALUES (?, ?, ?, ?, ?, NULL, ?)
    """, (lote, data_formatacao, data_hvi, safra, produtor, responsavel))

    conn.commit()
    id_formatacao = cursor.lastrowid
    conn.close()
    return id_formatacao

def inserir_fardos(formatacao_id, df, usuario_nome):
    conn = conectar()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        fardo_id = row.get("FardoID", "")
        mic = float(row.get("MIC", 0)) if str(row.get("MIC", "")).replace(".", "", 1).isdigit() else None
        uhml = float(row.get("UHML", 0)) if str(row.get("UHML", "")).replace(".", "", 1).isdigit() else None
        str_val = float(row.get("STR", 0)) if str(row.get("STR", "")).replace(".", "", 1).isdigit() else None
        sfi = float(row.get("SFI", 0)) if str(row.get("SFI", "")).replace(".", "", 1).isdigit() else None
        ui = float(row.get("UI", 0)) if str(row.get("UI", "")).replace(".", "", 1).isdigit() else None
        csp = float(row.get("CSP", 0)) if str(row.get("CSP", "")).replace(".", "", 1).isdigit() else None
        elg = float(row.get("ELG", 0)) if str(row.get("ELG", "")).replace(".", "", 1).isdigit() else None
        rd = float(row.get("Rd", 0)) if str(row.get("Rd", "")).replace(".", "", 1).isdigit() else None
        b = float(row.get("+b", 0)) if str(row.get("+b", "")).replace(".", "", 1).isdigit() else None
        trid = row.get("TrID", "")
        sci = float(row.get("SCI", 0)) if str(row.get("SCI", "")).replace(".", "", 1).isdigit() else None
        mat = float(row.get("MAT", 0)) if str(row.get("MAT", "")).replace(".", "", 1).isdigit() else None
        cg = row.get("CG", "")
        produtor = row.get("Produtor", "")
        tipo = row.get("Tipo", "")

        cursor.execute("""
            INSERT INTO fardos (
                formatacao_id, fardo_id, mic, uhml, str, sfi, ui, csp, elg,
                rd, b, trid, sci, mat, cg, produtor, tipo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            formatacao_id, fardo_id, mic, uhml, str_val, sfi, ui, csp, elg,
            rd, b, trid, sci, mat, cg, produtor, tipo
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
               fa.rd, fa.b, fa.trid, fa.sci, fa.mat, fa.cg, fa.produtor, fa.tipo, f.safra
        FROM fardos fa
        JOIN formatacoes f ON fa.formatacao_id = f.id
    """)
    colunas = [
        "Lote", "FardoID", "MIC", "UHML", "STR", "SFI", "UI", "CSP", "ELG",
        "Rd", "+b", "TrID", "SCI", "MAT", "CG", "Produtor", "Tipo", "Safra"
    ]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=colunas)
