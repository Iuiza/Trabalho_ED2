from flask import Flask, render_template, url_for, send_file
import gzip

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
    return render_template('etapa1.html', titulo = titulo, catalogo = catalogo)

@app.route('/download')
def download_file():
    with open('produtos.json', 'rb') as arquivo_original:
        with gzip.open('produtos.json.gz', 'wb') as arquivo_compactado:
            arquivo_compactado.write(arquivo_original.read())
    return send_file('produtos.json.gz', as_attachment=True)
    
if __name__ == "__main__":
    app.run(debug=True)