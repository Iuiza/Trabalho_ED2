import json
from BTreeBiblioteca import Registro, Pagina, _Insere, Pesquisa, Imprime, ImprimeMenor, ImprimeMaior

# Carregar o arquivo JSON
with open('produtos.json', 'r', encoding='utf-8') as file:
    dados = json.load(file)

# Função para inserir um item na árvore B
def inserir_na_arvore(arvore, chave, elemento, ordem):
    reg = Registro()
    reg.Chave = chave
    reg.Elemento = elemento
    arvore = _Insere(reg, arvore, ordem)
    return arvore

# Função para criar a árvore B a partir dos dados JSON
def criar_arvore(dados, ordem):
    arvore = None
    for categoria, itens in dados.items():
        for nome, detalhes in itens.items():
            chave = f"{categoria}-{nome}"
            arvore = inserir_na_arvore(arvore, chave, detalhes, ordem)
    return arvore

# Função para pesquisar um item na árvore B
def pesquisar_na_arvore(arvore, chave):
    reg = Registro()
    reg.Chave = chave
    resultado = Pesquisa(reg, arvore)
    if resultado:
        return resultado.Elemento
    else:
        return None

# Função para imprimir a árvore B em ordem
def imprimir_arvore_em_ordem(arvore):
    Imprime(arvore)

# Função para imprimir os registros menores que uma determinada chave
def imprimir_registros_menores(arvore, chave):
    reg = Registro()
    reg.Chave = chave
    ImprimeMenor(reg, arvore)

# Função para imprimir os registros maiores que uma determinada chave
def imprimir_registros_maiores(arvore, chave):
    reg = Registro()
    reg.Chave = chave
    ImprimeMaior(reg, arvore)

# Função para imprimir os registros entre um intervalo de chaves
def imprimir_registros_intervalo(arvore, chave_min, chave_max):
    reg_min = Registro()
    reg_max = Registro()
    reg_min.Chave = chave_min
    reg_max.Chave = chave_max
    imprimir_registros_menores_intervalo(arvore, reg_min, reg_max)

def imprimir_registros_menores_intervalo(arvore, reg_min, reg_max):
    if arvore is not None:
        i = 0
        while i < arvore.n:
            imprimir_registros_menores_intervalo(arvore.p[i], reg_min, reg_max)
            if reg_min.Chave <= arvore.r[i].Chave <= reg_max.Chave:
                print(f"Chave: {arvore.r[i].Chave}, Elemento: {arvore.r[i].Elemento}")
            i += 1
        imprimir_registros_menores_intervalo(arvore.p[i], reg_min, reg_max)

# Função para criar dois índices para dois campos do arquivo JSON
def criar_indices(dados, campo1, campo2, ordem):
    arvore1 = None
    arvore2 = None
    for categoria, itens in dados.items():
        for nome, detalhes in itens.items():
            if campo1 in detalhes:
                chave1 = f"{categoria}-{nome}-{campo1}"
                arvore1 = inserir_na_arvore(arvore1, chave1, detalhes[campo1], ordem)
            if campo2 in detalhes:
                chave2 = f"{categoria}-{nome}-{campo2}"
                arvore2 = inserir_na_arvore(arvore2, chave2, detalhes[campo2], ordem)
    return arvore1, arvore2

# Definir a ordem da árvore B
ordem = 4

# Criar a árvore B a partir dos dados JSON
arvore = criar_arvore(dados, ordem)

# Imprimir a árvore B em ordem
print("Árvore B em ordem:")
imprimir_arvore_em_ordem(arvore)
print("\n")

# Pesquisar um item na árvore B
chave_pesquisa = "camisa-Camisa Oversized"
elemento_encontrado = pesquisar_na_arvore(arvore, chave_pesquisa)
if elemento_encontrado:
    print(f"Elemento encontrado para a chave '{chave_pesquisa}': {elemento_encontrado}")
else:
    print(f"Elemento não encontrado para a chave '{chave_pesquisa}'")
print("\n")

# Imprimir registros menores que uma determinada chave
chave_menor = "camisa-Camisa Cropped"
print(f"Registros menores que a chave '{chave_menor}':")
imprimir_registros_menores(arvore, chave_menor)
print("\n")

# Imprimir registros maiores que uma determinada chave
chave_maior = "camisa-Camisa Tricotada"
print(f"Registros maiores que a chave '{chave_maior}':")
imprimir_registros_maiores(arvore, chave_maior)
print("\n")

# Imprimir registros entre um intervalo de chaves
chave_min = "camisa-Camisa Cropped"
chave_max = "camisa-Camisa Tricotada"
print(f"Registros entre as chaves '{chave_min}' e '{chave_max}':")
imprimir_registros_intervalo(arvore, chave_min, chave_max)
print("\n")

# Criar dois índices para dois campos do arquivo JSON
campo1 = "cor"
campo2 = "preco"
arvore1, arvore2 = criar_indices(dados, campo1, campo2, ordem)

print("Árvore B para o campo 'cor':")
imprimir_arvore_em_ordem(arvore1)
print("\n")

print("Árvore B para o campo 'preco':")
imprimir_arvore_em_ordem(arvore2)
print("\n")