import networkx as nx
import folium

# Criação do grafo dirigido
G = nx.DiGraph()

# Adicionando nós e arcos com pesos (distâncias em metros)
edges = [
    ('Barra', 'Ondina', 100), ('Ondina', 'Rio Vermelho', 150), ('Barra', 'Rio Vermelho', 250),
    ('Rio Vermelho', 'Pituba', 200), ('Ondina', 'Pituba', 300), ('Pituba', 'Amaralina', 100),
    ('Amaralina', 'Itaigara', 150), ('Itaigara', 'Brotas', 100), ('Brotas', 'Garcia', 250),
    ('Garcia', 'Canela', 200), ('Canela', 'Campo Grande', 300), ('Campo Grande', 'Comercio', 100),
    ('Comercio', 'Pelourinho', 150), ('Pelourinho', 'Sao Joaquim', 200), ('Sao Joaquim', 'Bonfim', 250),
    ('Bonfim', 'Ribeira', 300), ('Ribeira', 'Sao Caetano', 100), ('Sao Caetano', 'Liberdade', 150),
    ('Liberdade', 'Cabula', 200), ('Cabula', 'Pernambués', 250), ('Pernambués', 'Tancredo Neves', 300),
    ('Tancredo Neves', 'Iguatemi', 100), ('Iguatemi', 'Paralela', 150), ('Paralela', 'Stiep', 200),
    ('Stiep', 'Costa Azul', 250), ('Costa Azul', 'Armação', 300), ('Armação', 'Itapuã', 100)
]

for edge in edges:
    G.add_edge(edge[0], edge[1], weight=edge[2])

# Coordenadas de exemplo para os bairros
node_coords = {
    'Barra': [-13.0104, -38.5245], 'Ondina': [-13.0045, -38.5083], 'Rio Vermelho': [-12.9986, -38.5049],
    'Pituba': [-12.9994, -38.4603], 'Amaralina': [-12.9886, -38.4601], 'Itaigara': [-12.9835, -38.4606],
    'Brotas': [-12.9730, -38.4901], 'Garcia': [-12.9810, -38.5083], 'Canela': [-12.9780, -38.5124],
    'Campo Grande': [-12.9773, -38.5163], 'Comercio': [-12.9692, -38.5161], 'Pelourinho': [-12.9712, -38.5079],
    'Sao Joaquim': [-12.9505, -38.4858], 'Bonfim': [-12.9245, -38.5028], 'Ribeira': [-12.9095, -38.5048],
    'Sao Caetano': [-12.9250, -38.4810], 'Liberdade': [-12.9268, -38.4775], 'Cabula': [-12.9268, -38.4352],
    'Pernambués': [-12.9350, -38.4568], 'Tancredo Neves': [-12.9217, -38.4383], 'Iguatemi': [-12.9783, -38.4532],
    'Paralela': [-12.9297, -38.4415], 'Stiep': [-13.0023, -38.4501], 'Costa Azul': [-12.9897, -38.4395],
    'Armação': [-12.9778, -38.4348], 'Itapuã': [-12.9404, -38.3781]
}

# Função para adicionar arestas no mapa
def add_edge(map_obj, start, end, color='blue'):
    folium.PolyLine(
        [start, end],
        color=color,
        weight=2.5,
        opacity=1
    ).add_to(map_obj)

# Criação do mapa centrado em Salvador
m = folium.Map(location=[-12.9714, -38.5014], zoom_start=13)

# Adicionando as arestas no mapa
for edge in G.edges(data=True):
    start = node_coords[edge[0]]
    end = node_coords[edge[1]]
    add_edge(m, start, end)

# Adicionando os nós no mapa
for node, coords in node_coords.items():
    folium.Marker(location=coords, popup=node, icon=folium.Icon(color='red')).add_to(m)

# Salvando o mapa inicial em um arquivo HTML
m.save('mapa.html')

# Exemplo de produtos e preços
produtos = {
    'produto1': 50,
    'produto2': 30,
    'produto3': 20,
}

# Função para calcular o menor caminho
def calcular_frete(G, origem, destino):
    caminho = nx.shortest_path(G, source=origem, target=destino, weight='weight')
    distancia = nx.shortest_path_length(G, source=origem, target=destino, weight='weight')
    return caminho, distancia

# Interface básica de carrinho de compras
def carrinho_compras():
    carrinho = []
    while True:
        produto = input("Digite o produto que deseja adicionar ao carrinho (ou 'sair' para finalizar): ")
        if produto == 'sair':
            break
        elif produto in produtos:
            carrinho.append(produto)
            print(f"{produto} adicionado ao carrinho.")
        else:
            print("Produto não encontrado.")
    
    return carrinho

# Função principal
def main():
    carrinho = carrinho_compras()
    origem = input("Digite o ponto de origem: ")
    destino = input("Digite o ponto de destino: ")

    caminho, distancia = calcular_frete(G, origem, destino)
    custo_frete = distancia * 0.05  # Exemplo de política de custo de frete

    print(f"Caminho: {' -> '.join(caminho)}")
    print(f"Distância: {distancia} metros")
    print(f"Custo do frete: R${custo_frete:.2f}")

    total = sum(produtos[p] for p in carrinho) + custo_frete
    print(f"Total a pagar: R${total:.2f}")

    # Destacar o caminho no mapa
    m = folium.Map(location=[-12.9714, -38.5014], zoom_start=13)
    
    # Adicionando as arestas no mapa
    for edge in G.edges(data=True):
        start = node_coords[edge[0]]
        end = node_coords[edge[1]]
        add_edge(m, start, end)
    
    # Adicionando os nós no mapa
    for node, coords in node_coords.items():
        folium.Marker(location=coords, popup=node, icon=folium.Icon(color='red')).add_to(m)

    # Destacando o caminho no mapa
    for i in range(len(caminho) - 1):
        start = node_coords[caminho[i]]
        end = node_coords[caminho[i + 1]]
        add_edge(m, start, end, color='red')

    # Salvando o mapa atualizado em um arquivo HTML
    m.save('mapa.html')

if __name__ == "__main__":
    main()