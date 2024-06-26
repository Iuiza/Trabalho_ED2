import networkx as nx
import math

# Função para calcular a distância haversine entre duas coordenadas
def haversine(coord1, coord2):
    R = 6371  # Raio da Terra em km
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon1 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Criando o grafo
G = nx.DiGraph()

# Lista de bairros de Salvador (adicionando mais quatro bairros)
bairros = [
    "Barra", "Pituba", "Rio Vermelho", "Ondina", "Brotas",
    "Itaigara", "Stiep", "Caminho das Árvores", "Imbuí",
    "Paralela", "Patamares", "Piatã", "Stella Maris", 
    "Itapuã", "São Cristóvão", "Centro", "Comércio",
    "Bonfim", "Ribeira", "Liberdade", "Cabula",
    "Pernambués", "Boca do Rio", "São Marcos", "Pirajá"
]

# Adicionando nós ao grafo
G.add_nodes_from(bairros)

# Coordenadas fictícias para os bairros (substitua com dados reais)
node_coords = {
    "Barra": [-13.0105, -38.5085],
    "Pituba": [-12.9995, -38.4603],
    "Rio Vermelho": [-12.9913, -38.5107],
    "Ondina": [-13.0000, -38.5083],
    "Brotas": [-12.9718, -38.4877],
    "Itaigara": [-12.9821, -38.4644],
    "Stiep": [-12.9981, -38.4431],
    "Caminho das Árvores": [-12.9799, -38.4653],
    "Imbuí": [-12.9794, -38.4547],
    "Paralela": [-12.9782, -38.4598],
    "Patamares": [-12.9533, -38.4017],
    "Piatã": [-12.9391, -38.3825],
    "Stella Maris": [-12.9147, -38.3375],
    "Itapuã": [-12.9244, -38.3658],
    "São Cristóvão": [-12.9004, -38.3360],
    "Centro": [-12.9738, -38.5022],
    "Comércio": [-12.9690, -38.5140],
    "Bonfim": [-12.9401, -38.5041],
    "Ribeira": [-12.9265, -38.5120],
    "Liberdade": [-12.9364, -38.4855],
    "Cabula": [-12.9512, -38.4562],
    "Pernambués": [-12.9625, -38.4797],
    "Boca do Rio": [-12.9517, -38.4451],
    "São Marcos": [-12.9307, -38.4333],
    "Pirajá": [-12.9087, -38.4387]
}

# Adicionando arestas com pesos baseados na distância
for bairro in bairros:
    distances = []
    for other_bairro in bairros:
        if bairro != other_bairro:
            distance = haversine(node_coords[bairro], node_coords[other_bairro])
            distances.append((other_bairro, distance))
    distances.sort(key=lambda x: x[1])
    closest_three = distances[:3]
    for conn, dist in closest_three:
        G.add_edge(bairro, conn, weight=dist)

# Exemplo de como você pode acessar os dados do grafo
for node in G.nodes(data=True):
    print(node)
for edge in G.edges(data=True):
    print(edge)