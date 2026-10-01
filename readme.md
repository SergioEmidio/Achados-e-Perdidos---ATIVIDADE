# Achados e Perdidos

Mini app web para um mural de achados e perdidos, feito com **Python + Flask + SQLite**, com front-end em **HTML, CSS e JavaScript**.

## Funcionalidades

- Cadastrar item **perdido** ou **encontrado** (nome, descrição, local e contato)
- Visualizar os itens cadastrados em um mural
- Marcar item como **Resolvido** (e reabrir, se necessário)
- Filtrar: **Todos / Perdidos / Encontrados**
- Bônus: busca por palavra-chave, mensagens de feedback (toasts) e upload de imagem

## Como rodar

```bash
git clone <URL-DO-REPOSITORIO>
cd achados-e-perdidos

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Abra http://127.0.0.1:5000 no navegador. O banco `achados.db` é criado automaticamente na primeira execução.

## Estrutura

```
app.py              # rotas Flask, API JSON e banco SQLite
templates/index.html
static/style.css
static/script.js    # fetch na API, filtros, busca e feedback
uploads/            # imagens enviadas
requirements.txt
```

## API

| Método | Rota                          | Descrição                                  |
|--------|-------------------------------|--------------------------------------------|
| GET    | `/api/itens?tipo=&q=`         | Lista itens (`tipo`: todos/perdido/encontrado; `q`: busca) |
| POST   | `/api/itens`                  | Cadastra item (multipart, com imagem opcional) |
| PATCH  | `/api/itens/<id>/resolver`    | Alterna entre pendente e resolvido         |

## Tecnologias

Python 3, Flask, SQLite (módulo `sqlite3`), HTML5, CSS3 e JavaScript puro.