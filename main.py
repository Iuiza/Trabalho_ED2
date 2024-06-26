from flask import Flask, render_template, send_file, redirect, request, jsonify
import json
import logging
import BTreeBiblioteca
import pandas as pd
from io import StringIO
import sys
import networkx as nx
import folium
import os
import math

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

def inserir_na_arvore(arvore, chave, elemento, ordem):
    reg = BTreeBiblioteca.Registro()
    reg.Chave = chave
    reg.Elemento = elemento
    arvore = BTreeBiblioteca._Insere(reg, arvore, ordem)
    return arvore

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

catalogo = carregar_catalogo()

# Criação do grafo com distâncias reais aproximadas
G = nx.DiGraph()
edges = [
    ('Barra', 'Ondina', 2.5), ('Ondina', 'Rio Vermelho', 3.0), ('Barra', 'Rio Vermelho', 5.0),
    ('Rio Vermelho', 'Pituba', 4.0), ('Ondina', 'Pituba', 5.5), ('Pituba', 'Amaralina', 1.5),
    ('Amaralina', 'Itaigara', 2.0), ('Itaigara', 'Brotas', 2.5), ('Brotas', 'Garcia', 4.0),
    ('Garcia', 'Canela', 1.5), ('Canela', 'Campo Grande', 2.0), ('Campo Grande', 'Comercio', 2.5),
    ('Comercio', 'Pelourinho', 1.0), ('Pelourinho', 'Sao Joaquim', 2.0), ('Sao Joaquim', 'Bonfim', 3.0),
    ('Bonfim', 'Ribeira', 2.5), ('Ribeira', 'Sao Caetano', 4.0), ('Sao Caetano', 'Liberdade', 3.5),
    ('Liberdade', 'Cabula', 5.0), ('Cabula', 'Pernambués', 2.0), ('Pernambués', 'Tancredo Neves', 1.5),
    ('Tancredo Neves', 'Iguatemi', 2.0), ('Iguatemi', 'Paralela', 2.5), ('Paralela', 'Stiep', 3.0),
    ('Stiep', 'Costa Azul', 1.5), ('Costa Azul', 'Armação', 2.0), ('Armação', 'Itapuã', 6.0)
]
for edge in edges:
    G.add_edge(edge[0], edge[1], weight=edge[2])

# Coordenadas dos bairros e ponto central de distribuição
node_coords = {
    'Barra': [-13.0104, -38.5245], 'Ondina': [-13.0045, -38.5083], 'Rio Vermelho': [-12.9986, -38.5049],
    'Pituba': [-12.9994, -38.4603], 'Amaralina': [-12.9886, -38.4601], 'Itaigara': [-12.9835, -38.4606],
    'Brotas': [-12.9730, -38.4901], 'Garcia': [-12.9810, -38.5083], 'Canela': [-12.9780, -38.5124],
    'Campo Grande': [-12.9773, -38.5163], 'Comercio': [-12.9692, -38.5161], 'Pelourinho': [-12.9712, -38.5079],
    'Sao Joaquim': [-12.9505, -38.4858], 'Bonfim': [-12.9245, -38.5028], 'Ribeira': [-12.9095, -38.5048],
    'Sao Caetano': [-12.9250, -38.4810], 'Liberdade': [-12.9268, -38.4775], 'Cabula': [-12.9268, -38.4352],
    'Pernambués': [-12.9350, -38.4568], 'Tancredo Neves': [-12.9217, -38.4383], 'Iguatemi': [-12.9783, -38.4532],
    'Paralela': [-12.9297, -38.4415], 'Stiep': [-13.0023, -38.4501], 'Costa Azul': [-12.9897, -38.4395],
    'Armação': [-12.9778, -38.4348], 'Itapuã': [-12.9404, -38.3781], 'Central Distribuição': [-12.9730, -38.4901]
}

# Conectar a central de distribuição aos pontos mais próximos
G.add_edge('Central Distribuição', 'Barra', weight=3.0)
G.add_edge('Central Distribuição', 'Ondina', weight=2.5)
G.add_edge('Central Distribuição', 'Rio Vermelho', weight=2.0)
G.add_edge('Central Distribuição', 'Pernambués', weight=3)

def add_edge(map_obj, start, end, color='blue'):
    folium.PolyLine(
        [start, end],
        color=color,
        weight=2.5,
        opacity=1
    ).add_to(map_obj)

arvore_nome = None
chave_nome = 7
arvore_nome = BTreeBiblioteca.Inserir(arvore_nome, 1, criar_dataframe(), chave_nome)

arvore_preco = None
chave_preco = 5
arvore_preco = BTreeBiblioteca.Inserir(arvore_preco, 1, criar_dataframe(), chave_preco)

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

    chave = preco
    global arvore_preco
    arvore_preco = inserir_na_arvore(arvore_preco, chave, produto, ordem)

    adicionar_produto(produto, categoria, nome)
    
    return jsonify({"message": "Produto inserido com sucesso!"})

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    chave = request.form['chave-pesquisa']
    logging.debug(f"Pesquisando chave: {chave}")

    if (chave.isalpha()):
        elemento = pesquisar_na_arvore(arvore_nome, chave)
    else:
        chave = float(chave)
        elemento = pesquisar_na_arvore(arvore_preco, chave)

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

    if (chave.isalpha()):
        result = imprimir_registros_menores(arvore_nome, chave)
    else:
        chave = float(chave)
        result = imprimir_registros_menores(arvore_preco, chave)

    logging.debug("Registros menores impressos.")
    return jsonify({"status": "success", "resultado": result})

@app.route('/imprimir_maiores', methods=['POST'])
def maiores():
    chave = request.form['chave-maiores']
    logging.debug(f"Pesquisando registros maiores que a chave: {chave}")
    if (chave.isalpha()):
        result = imprimir_registros_maiores(arvore_nome, chave)
    else:
        chave = float(chave)
        result = imprimir_registros_maiores(arvore_preco, chave)

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
    if (chave_min.isalpha() and chave_max.isalpha()):
        imprimir_registros_intervalo(arvore_nome, chave_min, chave_max)
    else:
        chave_min = float(chave_min)
        chave_max = float(chave_max)
        imprimir_registros_intervalo(arvore_preco, chave_min, chave_max)
    
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

@app.route('/carrinho')
def carrinho_pagina():
    return render_template('carrinho.html', catalogo=catalogo, node_coords=node_coords)

@app.route('/calcular_frete', methods=['POST'])
def calcular_frete():
    destino = request.form['destino']
    origem = 'Central Distribuição'
    caminho, distancia = nx.shortest_path(G, source=origem, target=destino, weight='weight'), nx.shortest_path_length(G, source=origem, target=destino, weight='weight')
    custo_frete = distancia * 1

    # Criação do mapa
    m = folium.Map(location=[-12.9714, -38.5014], zoom_start=13)
    for edge in G.edges(data=True):
        start, end = node_coords[edge[0]], node_coords[edge[1]]
        add_edge(m, start, end)
    for node, coords in node_coords.items():
        folium.Marker(location=coords, popup=node, icon=folium.Icon(color='red')).add_to(m)
    for i in range(len(caminho) - 1):
        start, end = node_coords[caminho[i]], node_coords[caminho[i + 1]]
        add_edge(m, start, end, color='red')
    
    folium.Marker(location=node_coords['Central Distribuição'], popup='Central Distribuição', icon=folium.Icon(color='blue')).add_to(m)

    # Salvar o mapa na pasta templates
    mapa_path = os.path.join('templates', 'mapa.html')
    m.save(mapa_path)

    if not os.path.exists(mapa_path):
        return jsonify({"status": "error", "message": "Falha ao salvar o mapa."})

    return jsonify({"caminho": caminho, "distancia": distancia, "custo_frete": custo_frete, "mapa_url": "/mapa.html"})

@app.route('/mapa.html')
def mapa():
    return render_template('mapa.html')

if __name__ == "__main__":
    app.run(debug=True)