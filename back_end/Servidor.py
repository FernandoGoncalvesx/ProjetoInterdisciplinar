import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.dirname(PASTA_ATUAL)

PASTA_FRONTEND = os.path.join(PASTA_PROJETO, 'front_end')
PASTA_UPLOADS = os.path.join(PASTA_ATUAL, 'uploads')

os.makedirs(PASTA_UPLOADS, exist_ok=True)

app = Flask(__name__, static_folder=PASTA_FRONTEND)
CORS(app)  

# 2. Rota para carregar o seu index.html
@app.route('/')
def index():
    return send_from_directory(PASTA_FRONTEND, 'index.html')

# 3. Rota para carregar os arquivos estáticos (CSS e JS)
@app.route('/<path:path>')
def arquivos_estaticos(path):
    return send_from_directory(PASTA_FRONTEND, path)

# 4. Rota (API) para receber o upload das fotos
@app.route('/api/upload', methods=['POST'])
def upload_fotos():
    # Verifica se a requisição tem arquivos com o nome 'fotos'
    if 'fotos' not in request.files:
        return jsonify({'mensagem': 'Nenhuma foto enviada.'}), 400
    
    arquivos = request.files.getlist('fotos')
    arquivos_salvos = []
    
    for arquivo in arquivos:
        if arquivo.filename == '':
            continue
            
        # <--- NOVO: Limpa o nome do arquivo tirando caracteres perigosos ou caminhos falsos
        nome_seguro = secure_filename(arquivo.filename)
            
        # <--- NOVO: Usa o 'nome_seguro' em vez do nome original que o usuário mandou
        caminho_completo = os.path.join(PASTA_UPLOADS, nome_seguro)
        arquivo.save(caminho_completo)
        arquivos_salvos.append(nome_seguro)
            
    return jsonify({
        'mensagem': 'Fotos enviadas com sucesso!',
        'arquivos': arquivos_salvos
    }), 200

# Inicia o servidor na porta 5000
if __name__ == '__main__':
    print("Servidor rodando! Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)
