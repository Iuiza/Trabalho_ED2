from flask import Flask, render_template, url_for, send_file, redirect, request
import gzip
import json

app = Flask(__name__)

def carregar_catalogo():
    """Carrega o catálogo a partir do arquivo JSON."""
    with open('produtos.json', 'r') as f:
        catalogo = json.load(f)
    return catalogo

def salvar_catalogo(catalogo):
    """Salva o catálogo atualizado no arquivo JSON."""
    with open('produtos.json', 'w') as f:
        json.dump(catalogo, f, indent=4, ensure_ascii=False)

def adicionar_produto(produto, categoria, nome):
    """Adiciona um novo produto ao catálogo."""
    catalogo = carregar_catalogo()
    categoria = categoria
    produto_nome = nome
    if categoria not in catalogo:
        catalogo[categoria] = {}
    catalogo[categoria][produto_nome] = produto
    salvar_catalogo(catalogo)

def editar_produto(categoria, produto_nome, novo_produto):
    """Edita um produto existente no catálogo."""
    catalogo = carregar_catalogo()
    if categoria in catalogo and produto_nome in catalogo[categoria]:
        catalogo[categoria][produto_nome] = novo_produto
        salvar_catalogo(catalogo)
        return True
    return False

def remover_produto(categoria, produto_nome):
    """Remove um produto do catálogo."""
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
    titulo= "Catalogo"
    with open('produtos.json', 'r') as f:
        catalogo = json.load(f)
    return render_template('etapa1.html', titulo = titulo, catalogo = catalogo)

@app.route('/download')
def download_file():
    with open('produtos.json', 'rb') as arquivo_original:
        with gzip.open('produtos.json.gz', 'wb') as arquivo_compactado:
            arquivo_compactado.write(arquivo_original.read())
    return send_file('produtos.json.gz', as_attachment=True)

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

@app.route('/remover_produto', methods=['GET', 'POST'])
def remover_produto_pagina():
    if request.method == 'POST':
        categoria = request.form['categoria'].lower()
        produto_nome = request.form['nome']
        remover_produto(categoria, produto_nome)
        return redirect('/')
    return render_template('remover_produto.html')

if __name__ == "__main__":
    app.run(debug=True)