from flask import Flask, render_template, send_file, redirect, request, jsonify
import json

app = Flask(__name__)

def compress_rle(data):
    if not data:
        return ""

    compressed = []
    count = 1
    prev_char = data[0]

    for char in data[1:]:
        if char == prev_char:
            count += 1
        else:
            compressed.append(prev_char + str(count))
            prev_char = char
            count = 1

    compressed.append(prev_char + str(count))
    return ''.join(compressed)

def carregar_catalogo():
    with open('produtos.json', 'r') as f:
        catalogo = json.load(f)
    return catalogo

def salvar_catalogo(catalogo):
    with open('produtos.json', 'w') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)

def adicionar_produto(produto, categoria, nome):
    catalogo = carregar_catalogo()
    categoria = categoria
    produto_nome = nome
    if categoria not in catalogo:
        catalogo[categoria] = {}
    catalogo[categoria][produto_nome] = produto
    salvar_catalogo(catalogo)

def editar_produto(categoria, produto_nome, novo_produto):
    catalogo = carregar_catalogo()
    if categoria in catalogo and produto_nome in catalogo[categoria]:
        catalogo[categoria][produto_nome] = novo_produto
        salvar_catalogo(catalogo)
        return True
    return False

def remover_produto(categoria, produto_nome):
    catalogo = carregar_catalogo()
    if categoria in catalogo and produto_nome in catalogo[categoria]:
        del catalogo[categoria][produto_nome]
        salvar_catalogo(catalogo)
        return True
    return False

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route('/etapa1')
def sobre1():
    titulo = "Catalogo"
    with open('produtos.json', 'r') as f:
        catalogo = json.load(f)
    return render_template('etapa1.html', titulo=titulo, catalogo=catalogo)

@app.route('/compress_and_download', methods=['GET'])
def compress_and_download():
    catalogo = carregar_catalogo()
    json_string = json.dumps(catalogo)
    compressed_data = compress_rle(json_string)
    with open('compressed.json', 'w') as f:
        f.write(compressed_data)
    return send_file('compressed.json', as_attachment=True)

@app.route('/adicionar_produto', methods=['GET', 'POST'])
def adicionar_produto_pagina():
    if request.method == 'POST':
        categoria = request.form['categoria'].lower()
        nome = request.form['nome']
        produto = {
            "modelo": request.form['modelo'],
            "cor": request.form['cor'],
            "tecido": request.form['tecido'],
            "descricao": request.form['descricao'],
            "tamanhos": [tamanho.strip() for tamanho in request.form['tamanhos'].split(',')],
            "preco": float(request.form['preco'])
        }
        adicionar_produto(produto, categoria, nome)
        return redirect('/')
    return render_template('adicionar_produto.html')

@app.route('/editar_produto/<categoria>/<nome>', methods=['GET', 'POST'])
def editar_produto_pagina(categoria, nome):
    catalogo = carregar_catalogo()
    produto = catalogo.get(categoria, {}).get(nome)
    if request.method == 'POST':
        novo_produto = {
            "modelo": request.form['modelo'],
            "cor": request.form['cor'],
            "tecido": request.form['tecido'],
            "descricao": request.form['descricao'],
            "tamanhos": [tamanho.strip() for tamanho in request.form['tamanhos'].split(',')],
            "preco": float(request.form['preco'])
        }
        editar_produto(categoria, nome, novo_produto)
        return redirect('/')
    return render_template('editar_produto.html', produto=produto)

@app.route('/remover_produto/<categoria>/<nome>', methods=['GET', 'POST'])
def remover_produto_pagina(categoria, nome):
    if request.method == 'POST':
        remover_produto(categoria, nome)
        return redirect('/')
    catalogo = carregar_catalogo()
    produto = catalogo.get(categoria, {}).get(nome)
    return render_template('remover_produto.html', produto=produto)

if __name__ == "__main__":
    app.run(debug=True)
