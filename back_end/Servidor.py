import os
from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

# Caminhos baseados neste arquivo permitem iniciar a aplicação fora da pasta back_end.
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_PROJETO = os.path.dirname(PASTA_ATUAL)
load_dotenv(os.path.join(PASTA_PROJETO, '.env'))

PASTA_FRONTEND = os.path.join(PASTA_PROJETO, 'front_end')
PASTA_UPLOADS = os.path.join(PASTA_ATUAL, 'uploads')

# Suporta tanto `python back_end\Servidor.py` quanto `back_end.Servidor:app`.
if __package__:
    from .models.banco import conectar_banco
else:
    from models.banco import conectar_banco

# Uploads ficam fora do frontend para não serem publicados como arquivos estáticos.
os.makedirs(PASTA_UPLOADS, exist_ok=True)

# static_folder também registra /front_end/<arquivo>. Os HTMLs usam as rotas abaixo;
# essa rota adicional do Flask não é referenciada pela navegação atual.
app = Flask(__name__, static_folder=PASTA_FRONTEND)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv(
    'SESSION_COOKIE_SECURE', 'false'
).lower() == 'true'
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

# Confere a senha no servidor e mantém a identidade na sessão assinada pelo Flask.
@app.route('/api/login', methods=['POST'])
def login():
    if not app.config['SECRET_KEY']:
        return jsonify({'mensagem': 'Login indisponível: configure FLASK_SECRET_KEY no .env.'}), 503

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({'mensagem': 'Envie email e senha em formato JSON.'}), 400

    email = dados.get('email')
    senha = dados.get('senha')
    if not isinstance(email, str) or not isinstance(senha, str):
        return jsonify({'mensagem': 'Informe um email e uma senha válidos.'}), 400

    email = email.strip()
    if not email or not senha:
        return jsonify({'mensagem': 'Informe um email e uma senha válidos.'}), 400

    with conectar_banco() as conexao:
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT id, senha_hash FROM usuarios WHERE email = %s LIMIT 1',
                (email,),
            )
            usuario = cursor.fetchone()

    if not usuario or not check_password_hash(usuario['senha_hash'], senha):
        return jsonify({'mensagem': 'Email ou senha incorretos.'}), 401

    session.clear()
    session['usuario_id'] = usuario['id']
    return jsonify({'redirect': '/'})

# Recebe arquivos no disco; ainda não relaciona fotos a usuários nem consulta o MySQL.
# A rota está disponível, mas index.html está sem action e styles.js bloqueia seu envio.
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

# Apenas para desenvolvimento local. O Waitress importa app e não executa este bloco;
# isso é um ponto de entrada alternativo, não código morto.
if __name__ == '__main__':
    print("Servidor rodando! Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)
