from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route('/etapa1')
def sobre1():
    titulo = "Produtos"
    produtos = [
        {"nome": "Cadeira", "quantidade": 8},
        {"nome": "Cafeteira", "quantidade": 4},
        {"nome": "Mixer", "quantidade": 6},
        {"nome": "Cadeira", "quantidade": 8},
        {"nome": "Cafeteira", "quantidade": 4},
        {"nome": "Mixer", "quantidade": 6},
        {"nome": "Cadeira", "quantidade": 8},
        {"nome": "Cafeteira", "quantidade": 4},
        {"nome": "Mixer", "quantidade": 6},
        {"nome": "Cadeira", "quantidade": 8},
        {"nome": "Cafeteira", "quantidade": 4},
        {"nome": "Mixer", "quantidade": 6}
    ]
    return render_template('etapa1.html', titulo = titulo, produtos = produtos)
    
if __name__ == "__main__":
    app.run(debug=True)