import os
import sqlite3
import uuid
from datetime import datetime

from flask import Flask, g, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "achados.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EXTENSOES = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 4 MB por upload
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------- Banco de dados ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK (tipo IN ('perdido', 'encontrado')),
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                local TEXT NOT NULL,
                contato TEXT NOT NULL,
                imagem TEXT,
                resolvido INTEGER NOT NULL DEFAULT 0,
                criado_em TEXT NOT NULL
            )"""
        )


def item_para_dict(row):
    d = dict(row)
    d["resolvido"] = bool(d["resolvido"])
    d["imagem_url"] = f"/uploads/{d['imagem']}" if d["imagem"] else None
    return d


# ---------- Páginas ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploads/<path:arquivo>")
def uploads(arquivo):
    return send_from_directory(UPLOAD_DIR, arquivo)


# ---------- API ----------
@app.get("/api/itens")
def listar_itens():
    tipo = request.args.get("tipo", "todos")
    busca = request.args.get("q", "").strip()

    sql = "SELECT * FROM itens WHERE 1=1"
    params = []
    if tipo in ("perdido", "encontrado"):
        sql += " AND tipo = ?"
        params.append(tipo)
    if busca:
        sql += " AND (nome LIKE ? OR descricao LIKE ? OR local LIKE ?)"
        params += [f"%{busca}%"] * 3
    sql += " ORDER BY resolvido ASC, id DESC"

    linhas = get_db().execute(sql, params).fetchall()
    return jsonify([item_para_dict(r) for r in linhas])


@app.post("/api/itens")
def criar_item():
    f = request.form
    tipo = f.get("tipo", "").strip()
    campos = {k: f.get(k, "").strip() for k in ("nome", "descricao", "local", "contato")}

    if tipo not in ("perdido", "encontrado"):
        return jsonify(erro="Escolha se o item foi perdido ou encontrado."), 400
    faltando = [k for k, v in campos.items() if not v]
    if faltando:
        return jsonify(erro="Preencha todos os campos obrigatórios."), 400

    nome_arquivo = None
    arquivo = request.files.get("imagem")
    if arquivo and arquivo.filename:
        ext = secure_filename(arquivo.filename).rsplit(".", 1)[-1].lower()
        if ext not in EXTENSOES:
            return jsonify(erro="Envie uma imagem PNG, JPG, GIF ou WEBP."), 400
        nome_arquivo = f"{uuid.uuid4().hex}.{ext}"
        arquivo.save(os.path.join(UPLOAD_DIR, nome_arquivo))

    db = get_db()
    cur = db.execute(
        "INSERT INTO itens (tipo, nome, descricao, local, contato, imagem, criado_em) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tipo, campos["nome"], campos["descricao"], campos["local"], campos["contato"],
         nome_arquivo, datetime.now().strftime("%d/%m/%Y %H:%M")),
    )
    db.commit()
    row = db.execute("SELECT * FROM itens WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(item_para_dict(row)), 201


@app.patch("/api/itens/<int:item_id>/resolver")
def alternar_resolvido(item_id):
    db = get_db()
    row = db.execute("SELECT * FROM itens WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify(erro="Item não encontrado."), 404
    db.execute("UPDATE itens SET resolvido = ? WHERE id = ?", (0 if row["resolvido"] else 1, item_id))
    db.commit()
    row = db.execute("SELECT * FROM itens WHERE id = ?", (item_id,)).fetchone()
    return jsonify(item_para_dict(row))


@app.errorhandler(413)
def arquivo_grande(_e):
    return jsonify(erro="A imagem deve ter no máximo 4 MB."), 413


init_db()

if __name__ == "__main__":
    app.run(debug=True)