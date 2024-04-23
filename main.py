from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route('/etapa1')
def sobre1():
    titulo= "Catalogo"
    import json

    # Abra o arquivo JSON
    with open('produtos.json', 'r') as f:
        # Carregue o conteúdo do arquivo JSON como um dicionário
        catalogo = json.load(f)

    # Agora 'data' é um dicionário contendo o conteúdo do arquivo JSON
    # print(catalogo)


    # catalogo = [
    #     {"nome": "Cadeira", "quantidade": 8},
    #     {"nome": "Cafeteira", "quantidade": 4},
    #     {"nome": "Mixer", "quantidade": 6},
    # ]
    return render_template('etapa1.html', titulo = titulo, catalogo = catalogo)
    
if __name__ == "__main__":
    app.run(debug=True)