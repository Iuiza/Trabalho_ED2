import pandas as pd
import json
import BTreeBiblioteca

# Carregar o arquivo JSON
with open('produtos.json', 'r') as f:
    data = json.load(f)

# Lista para armazenar os dados normalizados
data_list = []

# Iterar sobre os dados para converter em uma estrutura tabular
for categoria, produtos in data.items():
    for nome, detalhes in produtos.items():
        detalhes['categoria'] = categoria
        detalhes['nome'] = nome
        data_list.append(detalhes)

# Usar pd.json_normalize para converter o JSON em um DataFrame
df = pd.json_normalize(data_list)

# Exibir o DataFrame
print(df)

ap = None
chave = 1
x = 7 # 5 - preço

ap = BTreeBiblioteca.Inserir(ap, chave, df, x)

BTreeBiblioteca.Imprime(ap)