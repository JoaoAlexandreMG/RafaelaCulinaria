from flask import Flask, request, jsonify, render_template
import os
import ast
import json
import requests
from sqlalchemy import create_engine, text

app = Flask(__name__)


# Configuração da conexão com o banco de dados usando SQLAlchemy
def conectar_bd():
    DATABASE_URL = (
        "postgresql+psycopg2://postgres:2584@localhost:5432/rafaela_culinaria"
    )
    engine = create_engine(DATABASE_URL, echo=True, client_encoding="utf8")
    return engine.connect()


# Função para obter preços do banco de dados
def obter_precos(itens_pedido):
    subtotal = []
    conexao = conectar_bd()

    # Lista de tabelas para pesquisa
    tabelas = [
        "bolos",
        "doces",
        "paes",
        "salgados_assados",
        "salgados_fritos",
        "tortas_salgadas",
        "variados",
    ]

    for quantidade, nome_produto in itens_pedido:
        preco_unitario = None
        # Percorrer todas as tabelas
        for tabela in tabelas:
            query = text(
                f"SELECT nome, preco FROM {tabela} WHERE LOWER(nome) = LOWER(:nome_produto);"
            )
            resultado = conexao.execute(
                query, {"nome_produto": nome_produto}
            ).fetchone()
            if resultado:
                nome_produto_bd, preco = resultado
                preco_unitario = preco
                break  # Produto encontrado, sair do loop de tabelas

        if preco_unitario is not None:
            subtotal.append(
                {
                    "produto": nome_produto,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario,
                    "subtotal": preco_unitario * quantidade,
                }
            )
        else:
            print(f"Produto não encontrado: {nome_produto}")

    conexao.close()
    return subtotal


# Função para processar a string de entrada
def processar_string_entrada(string_entrada):
    try:
        itens_pedido = ast.literal_eval(string_entrada)
        if not isinstance(itens_pedido, list) or not all(
            isinstance(i, tuple) and len(i) == 2 for i in itens_pedido
        ):
            raise ValueError("Formato de dados inválido")
        return obter_precos(itens_pedido)
    except Exception as e:
        print(f"Erro ao processar a string de entrada: {e}")
        return []


# Rota principal para renderizar o formulário
@app.route("/")
def index():
    return render_template("index.html")


# Rota para processar o pedido
@app.route("/processar_pedido", methods=["POST"])
def processar_pedido():
    pedido = request.form.get("pedido")
    print("Esse foi o pedido:", pedido)

    GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyCfWMm_C-pibdDJS2o5Oe2DaL2S-iN9Hrw"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Esse foi o pedido da cliente: {pedido}. Preciso que você associe cada item do pedido com os nomes exatos dos produtos listados abaixo. Considere os seguintes produtos disponíveis no banco de dados:\n"
                            "1/2 Pão de metro (Atum)\n"
                            "1/2 Pão de metro (Frango)\n"
                            "1/2 Pão de metro (Queijo/Presunto)\n"
                            "Apimentado\n"
                            "Barquete de bacalhau\n"
                            "Barquete de camarão\n"
                            "Barquete de frango\n"
                            "Beijinho\n"
                            "Bem casado\n"
                            "Bolinha de queijo\n"
                            "Bolinho de bacalhau\n"
                            "Bolinho de carne seca\n"
                            "Bolinho de feijoada\n"
                            "Bolinho de pizza\n"
                            "Boliviano\n"
                            "Bolo para café c/ cobertura\n"
                            "Bolo para café s/ cobertura\n"
                            "Bombom de nozes\n"
                            "Bombom francês\n"
                            "Brigadeiro\n"
                            "Camarão encapotado\n"
                            "Coxinha\n"
                            "Coxinha de abóbora e carne seca\n"
                            "Empada de frango\n"
                            "Enroladinho de salsicha\n"
                            "Esfiha\n"
                            "Fofinho de calabresa\n"
                            "Kibe\n"
                            "Mini Hamburguer\n"
                            "Mini pizza\n"
                            "Mini Sanduiche Natural (Atum)\n"
                            "Mini Sanduiche Natural (Frango)\n"
                            "Morango coberto\n"
                            "Ninho\n"
                            "Olho de sogra espelhado\n"
                            "Ovo de codorna surpresa\n"
                            "Paçoca\n"
                            "Pão de metro (Atum)\n"
                            "Pão de metro (Frango)\n"
                            "Pão de metro (Queijo/Presunto)\n"
                            "Pão de queijo\n"
                            "Pastel de forno (Bacalhau)\n"
                            "Pastel de forno (Frango)\n"
                            "Pastel Doce\n"
                            "Pastel Frito (Carne / Frango)\n"
                            "Pizza brotinho\n"
                            "Quiche\n"
                            "Rabo de tatu de forno\n"
                            "Risole de camarão\n"
                            "Saltenha\n"
                            "Torta salgada (Bacalhau) 25cm\n"
                            "Torta salgada (Bacalhau) 30cm\n"
                            "Torta salgada (Camarão) 25cm\n"
                            "Torta salgada (Camarão) 30cm\n"
                            "Torta salgada (Carne Seca) 25cm\n"
                            "Torta salgada (Carne Seca) 30cm\n"
                            "Torta salgada (Frango) 25cm\n"
                            "Torta salgada (Frango) 30cm\n"
                            "Tortelete de frango\n"
                            "Tropical\n"
                            "Uva coberta\n"
                            "Vermelhinho\n\n"
                            "Assegure-se de associar os itens de forma precisa e única, sem repetir produtos ou duplicar quantidades. Se um produto aparecer mais de uma vez no pedido, some as quantidades.\n"
                            "A saída deve seguir o seguinte formato estritamente:\n"
                            '[(quantidade_do_produto1, "produto1"), (quantidade_do_produto2, "produto2")]'
                        )
                    }
                ]
            }
        ]
    }

    # Requisição à API do Gemini
    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(data))

    # Processar resposta da API
    texto_resposta = (
        response.json()
        .get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )
    print(texto_resposta)
    subtotais = processar_string_entrada(texto_resposta)
    total = sum(item["subtotal"] for item in subtotais)
    # Formatação personalizada do pedido
    pedido_formatado = "---\nPedido de Salgados - Rafaela Culinária\n\n"
    for idx, item in enumerate(subtotais, start=1):
        pedido_formatado += f"{idx}. {item['produto']}\n"
        pedido_formatado += f"   - Quantidade: {item['quantidade']} unidades\n"
        pedido_formatado += f"   - Preço Unitário: R$ {item['preco_unitario']:.2f}\n"
        pedido_formatado += f"   - Subtotal: R$ {item['subtotal']:.2f}\n\n"

    pedido_formatado += "---\n"
    pedido_formatado += f"Total do Pedido:  R$ {total:.2f}\n"
    pedido_formatado += "---\n\n"
    pedido_formatado += (
        "Se precisar de alguma alteração ou tiver dúvidas, estou à disposição!"
    )

    return jsonify({"texto_retorno": pedido_formatado})


if __name__ == "__main__":
    app.run(debug=True)
