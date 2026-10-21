import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Caminhos baseados neste arquivo permitem iniciar a aplicação fora da pasta back_end.
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.dirname(PASTA_ATUAL)

PASTA_FRONTEND = os.path.join(PASTA_PROJETO, 'front_end')
PASTA_UPLOADS = os.path.join(PASTA_ATUAL, 'uploads')

# Uploads ficam fora do frontend para não serem publicados como arquivos estáticos.
os.makedirs(PASTA_UPLOADS, exist_ok=True)

app = Flask(__name__, static_folder=PASTA_FRONTEND)
# A política atual permite outras origens; deve ser restringida na implantação definitiva.
CORS(app)  

# As páginas são entregues como HTML estático, sem renderização de templates.
@app.route('/')
def index():
    return send_from_directory(PASTA_FRONTEND, 'index.html')

# A busca fica limitada à pasta do frontend; arquivos ausentes resultam em 404.
@app.route('/<path:path>')
def arquivos_estaticos(path):
    return send_from_directory(PASTA_FRONTEND, path)

# Recebe arquivos no disco; ainda não relaciona fotos a usuários nem consulta o MySQL.
@app.route('/api/upload', methods=['POST'])
def upload_fotos():
    # O nome do campo deve coincidir com o FormData enviado pela página inicial.
    if 'fotos' not in request.files:
        return jsonify({'mensagem': 'Nenhuma foto enviada.'}), 400
    
    # getlist permite receber vários arquivos com o mesmo nome de campo multipart.
    arquivos = request.files.getlist('fotos')
    arquivos_salvos = []
    
    for arquivo in arquivos:
        if arquivo.filename == '':
            continue
            
        # Normaliza o nome, mas não valida o conteúdo da imagem nem garante exclusividade.
        nome_seguro = secure_filename(arquivo.filename)
            
        # Nomes repetidos podem sobrescrever arquivos; o upload ainda precisa de validação
        # de conteúdo, limite de tamanho e identificação única antes do uso público contínuo.
        caminho_completo = os.path.join(PASTA_UPLOADS, nome_seguro)
        arquivo.save(caminho_completo)
        arquivos_salvos.append(nome_seguro)
            
    return jsonify({
        'mensagem': 'Fotos enviadas com sucesso!',
        'arquivos': arquivos_salvos
    }), 200

# Apenas para desenvolvimento local. O Waitress importa app e não executa este bloco.
if __name__ == '__main__':
    print("Servidor rodando! Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)
