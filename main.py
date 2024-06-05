from flask import Flask, render_template, send_file, redirect, request, jsonify
import json
import logging
import BTreeBiblioteca
import pandas as pd
from io import StringIO
import sys

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

with open('produtos.json', 'r', encoding='utf-8') as file:
    dados = json.load(file)

ordem = 4
arvore = None

def carregar_catalogo():
    with open('produtos.json', 'r') as f:
        catalogo = json.load(f)
    return catalogo

def inserir_na_arvore(arvore_nome, chave, elemento, ordem):
    reg = BTreeBiblioteca.Registro()
    reg.Chave = chave
    reg.Elemento = elemento
    arvore_nome = BTreeBiblioteca._Insere(reg, arvore_nome, ordem)
    return arvore_nome

def criar_arvore(dados, ordem):
    arvore = None
    
    for categoria, itens in dados.items():
        for nome, detalhes in itens.items():
            chave = f"{categoria}-{nome}"
            arvore = inserir_na_arvore(arvore, chave, detalhes, ordem)
    return arvore

def pesquisar_na_arvore(arvore, chave):
    reg = BTreeBiblioteca.Registro()
    reg.Chave = chave
    resultado = BTreeBiblioteca.Pesquisa(reg, arvore)
    if resultado:
        return resultado.Elemento
    else:
        return None

def imprimir_toda_arvore(arvore):
    output = StringIO()
    sys.stdout = output
    BTreeBiblioteca.Imprime(arvore)
    sys.stdout = sys.__stdout__
    result = output.getvalue()
    output.close()
    return result

def imprimir_registros_menores(arvore, chave):
    output = StringIO()
    sys.stdout = output
    reg = BTreeBiblioteca.Registro()
    reg.Chave = chave
    BTreeBiblioteca.ImprimeMenor(reg, arvore)
    sys.stdout = sys.__stdout__
    result = output.getvalue()
    output.close()
    return result

def imprimir_registros_maiores(arvore, chave):
    output = StringIO()
    sys.stdout = output
    reg = BTreeBiblioteca.Registro()
    reg.Chave = chave
    BTreeBiblioteca.ImprimeMaior(reg, arvore)
    sys.stdout = sys.__stdout__
    result = output.getvalue()
    output.close()
    return result

def imprimir_registros_intervalo(arvore, chave_min, chave_max):
    reg_min = BTreeBiblioteca.Registro()
    reg_max = BTreeBiblioteca.Registro()
    reg_min.Chave = chave_min
    reg_max.Chave = chave_max
    imprimir_registros_menores_intervalo(arvore, reg_min, reg_max)

def imprimir_registros_menores_intervalo(arvore, reg_min, reg_max):
    if arvore is not None:
        i = 0
        while i < arvore.n:
            imprimir_registros_menores_intervalo(arvore.p[i], reg_min, reg_max)
            if reg_min.Chave <= arvore.r[i].Chave <= reg_max.Chave:
                print(f"Chave: {arvore.r[i].Chave}, Posição: {arvore.r[i].Elemento}")
            i += 1
        imprimir_registros_menores_intervalo(arvore.p[i], reg_min, reg_max)

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

def criar_dataframe():
    data = carregar_catalogo()
    data_list = []

    for categoria, produtos in data.items():
        for nome, detalhes in produtos.items():
            detalhes['categoria'] = categoria
            detalhes['nome'] = nome
            data_list.append(detalhes)

    df = pd.json_normalize(data_list)

    return df

chave_nome = 7
arvore_nome = BTreeBiblioteca.Inserir(arvore, 1, criar_dataframe(), chave_nome)

chave_preco = 5
arvore_preco = BTreeBiblioteca.Inserir(arvore, 1, criar_dataframe(), chave_preco)

@app.route('/etapa2')
def etapa2():
    return render_template('etapa2.html')

@app.route('/inserir', methods=['POST'])
def inserir():
    categoria = request.form['categoria'].lower()
    nome = request.form['nome']
    modelo = request.form['modelo']
    cor = request.form['cor']
    tecido = request.form['tecido']
    descricao = request.form['descricao']
    tamanhos = request.form['tamanhos'].split(',')
    preco = float(request.form['preco'])

    produto = {
        "modelo": modelo,
        "cor": cor,
        "tecido": tecido,
        "descricao": descricao,
        "tamanhos": tamanhos,
        "preco": preco
    }

    chave = nome
    global arvore_nome
    arvore_nome = inserir_na_arvore(arvore_nome, chave, produto, ordem)
    adicionar_produto(produto, categoria, nome)
    
    return jsonify({"message": "Produto inserido com sucesso!"})

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    chave = request.form['chave-pesquisa']
    logging.debug(f"Pesquisando chave: {chave}")
    elemento = pesquisar_na_arvore(arvore_nome, chave)
    if elemento:
        logging.debug(f"Elemento encontrado: {elemento}")
        return jsonify({"Posição no dataframe": elemento})
    else:
        logging.debug(f"Elemento não encontrado: {chave}")
        return jsonify({"status": "error", "message": "Elemento não encontrado."})

@app.route('/imprimir', methods=['GET'])
def imprimir_arvore():
    resultado = imprimir_toda_arvore(arvore_nome)
    return jsonify({"resultado": resultado})

@app.route('/imprimir_menores', methods=['POST'])
def menores():
    chave = request.form['chave-menores']
    logging.debug(f"Pesquisando registros menores que a chave: {chave}")
    result = imprimir_registros_menores(arvore_nome, chave)
    logging.debug("Registros menores impressos.")
    return jsonify({"status": "success", "resultado": result})

@app.route('/imprimir_maiores', methods=['POST'])
def maiores():
    chave = request.form['chave-maiores']
    logging.debug(f"Pesquisando registros maiores que a chave: {chave}")
    result = imprimir_registros_maiores(arvore_nome, chave)
    logging.debug("Registros maiores impressos.")
    return jsonify({"status": "success", "resultado": result})

@app.route('/imprimir_intervalo', methods=['POST'])
def intervalo():
    chave_min = request.form['chave-min']
    chave_max = request.form['chave-max']
    logging.debug(f"Pesquisando intervalo: chave_min={chave_min}, chave_max={chave_max}")
    from io import StringIO
    import sys
    output = StringIO()
    sys.stdout = output
    imprimir_registros_intervalo(arvore_nome, chave_min, chave_max)
    sys.stdout = sys.__stdout__
    result = output.getvalue()
    output.close()
    logging.debug("Intervalo de registros impresso.")
    return jsonify({"status": "success", "resultado": result})

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