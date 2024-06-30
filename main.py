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
    ('Barra', 'Ondina', 3.0),
    ('Federação', 'Pituba', 8.3), ('Pituba', 'Amaralina', 1.9),
    ('Amaralina', 'Pituba', 2.6), ('Centro de Distribuição', 'Garcia', 5.0), ('Canela', 'Campo Grande', 1.3), ('Campo Grande', 'Comércio', 2.6),
    ('Comércio', 'Pelourinho', 1.0), ('Pelourinho', 'São Joaquim', 3.3),
    ('Bonfim', 'Ribeira', 1.5), ('Ribeira', 'São Caetano', 5.4), ('São Caetano', 'Liberdade', 3.4),
    ('Cabula', 'Mata Escura', 4.5), ('Mata Escura', 'Tancredo Neves', 2.4), ('Iguatemi', 'Paralela', 8.5),
    ('Stiep', 'Costa Azul', 2.4), ('Costa Azul', 'Armação', 2.7), ('Armação', 'Itapuã', 11.0), ('Stiep', 'Pituaçu', 6.0), ('Pituaçu', 'Itapuã', 10.0)
]
for edge in edges:
    G.add_edge(edge[0], edge[1], weight=edge[2])

# Coordenadas dos bairros e ponto central de distribuição
node_coords = {
    'Barra': [-13.005652530542964, -38.52780933712625], 'Ondina': [-13.005977431991946, -38.50992492411173], 'Federação': [-12.995376180538537, -38.5049512367971],
    'Pituba': [-13.002703583595409, -38.459863424415985], 'Amaralina': [-13.011787437300079, -38.47160216063372], 'Itaigara': [-12.993658715961963, -38.46473007998844],
    'Garcia': [-12.990992922926008, -38.512450771566854], 'Canela': [-12.991986253879722, -38.52156460867855],
    'Campo Grande': [-12.98563351173232, -38.509495318939464], 'Comércio': [-12.97158469776923, -38.51500288111888], 'Pelourinho': [-12.97292044772543, -38.50965557848379],
    'São Joaquim': [-12.977509297043566, -38.50118688936285], 'Bonfim': [-12.926656290216041, -38.50889348863223], 'Ribeira': [-12.919464349829349, -38.49932895248588],
    'São Caetano': [-12.935037881129835, -38.47459603205215], 'Liberdade': [-12.949600058248876, -38.49621511923113], 'Cabula': [-12.957646369437148, -38.46574007507009],
    'Mata Escura': [-12.934898514597188, -38.46122679546185], 'Tancredo Neves': [-12.94365629731757, -38.44960772747223], 'Iguatemi': [-12.981096062637421, -38.464985710659946],
    'Paralela': [-12.938183940894238, -38.41129642149876], 'Stiep': [-12.98116502808459, -38.44627487718024], 'Costa Azul': [-12.99379864448179, -38.44580398425715],
    'Armação': [-12.987193613034083, -38.438775409890305], 'Itapuã': [-12.937124674823417, -38.36117419076328], 'Pituaçu': [-12.958324082515647, -38.417501155339], 'Centro de Distribuição': [-12.972218589441002, -38.48860390331182]
}

# Conectar a central de distribuição aos pontos mais próximos
G.add_edge('Centro de Distribuição', 'Iguatemi', weight=4.4)
G.add_edge('Centro de Distribuição', 'Federação', weight=6.0)
G.add_edge('Centro de Distribuição', 'São Joaquim', weight=1.8)
G.add_edge('Centro de Distribuição', 'Cabula', weight=3.9)
G.add_edge('Barra', 'Federação', weight=4.6)
G.add_edge('Barra', 'Canela', weight=3.2)
G.add_edge('Ondina', 'Barra', weight=2.9)
G.add_edge('Federação', 'Ondina', weight=2.5)
G.add_edge('Federação', 'Barra', weight=4.6)
G.add_edge('Federação', 'Canela', weight=3.0)
G.add_edge('Pituba', 'Costa Azul', weight=3.0)
G.add_edge('Pituba', 'Federação', weight=7.0)
G.add_edge('Amaralina', 'Ondina', weight=5.0)
G.add_edge('Itaigara', 'Pituba', weight=2.1)
G.add_edge('Itaigara', 'Iguatemi', weight=1.8)
G.add_edge('Iguatemi', 'Itaigara', weight=2.0)
G.add_edge('Garcia', 'Barra', weight=3.4)
G.add_edge('Garcia', 'Campo Grande', weight=2.0)
G.add_edge('Canela', 'Barra', weight=3.4)
G.add_edge('Campo Grande', 'São Joaquim', weight=3.8)
G.add_edge('Pelourinho', 'Comércio', weight=1.0)
G.add_edge('São Joaquim', 'Liberdade', weight=3.8)
G.add_edge('São Joaquim', 'Pelourinho', weight=2.0)
G.add_edge('São Joaquim', 'Campo Grande', weight=4.0)
G.add_edge('São Caetano', 'Mata Escura', weight=4.0)
G.add_edge('Liberdade', 'São Caetano', weight=3.4)
G.add_edge('Liberdade', 'Mata Escura', weight=6.0)
G.add_edge('Liberdade', 'Bonfim', weight=6.0)
G.add_edge('Mata Escura', 'São Caetano', weight=4.0)
G.add_edge('Tancredo Neves', 'Paralela', weight=6.5)
G.add_edge('Iguatemi', 'Costa Azul', weight=3.5)
G.add_edge('Paralela', 'Itapuã', weight=7.0)
G.add_edge('Paralela', 'Pituaçu', weight=5.0)
G.add_edge('Costa Azul', 'Stiep', weight=3.0)
G.add_edge('Itapuã', 'Pituaçu', weight=9.0)
G.add_edge('Pituaçu', 'Stiep', weight=7.0)

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
    origem = 'Centro de Distribuição'
    caminho, distancia = nx.shortest_path(G, source=origem, target=destino, weight='weight'), nx.shortest_path_length(G, source=origem, target=destino, weight='weight')
    custo_frete = distancia * 1.5
    VELOCIDADE_MEDIA = 20 
    tempo_entrega = distancia / VELOCIDADE_MEDIA

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
    
    folium.Marker(location=node_coords['Centro de Distribuição'], popup='Centro de Distribuição', icon=folium.Icon(color='blue')).add_to(m)

    # Salvar o mapa na pasta templates
    mapa_path = os.path.join('templates', 'mapa.html')
    m.save(mapa_path)

    if not os.path.exists(mapa_path):
        return jsonify({"status": "error", "message": "Falha ao salvar o mapa."})

    return jsonify({"caminho": caminho, "distancia": distancia, "custo_frete": custo_frete, "mapa_url": "/mapa.html", 'tempo_entrega': tempo_entrega * 60})

@app.route('/mapa.html')
def mapa():
    return render_template('mapa.html')

if __name__ == "__main__":
    app.run(debug=True)