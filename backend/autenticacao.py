import secrets

from flask import Blueprint, flash, redirect, request, session, url_for
from mysql.connector import Error as ErroBanco, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.banco import conectar_banco

autenticacao = Blueprint("autenticacao", __name__)
HASH_AUSENTE = generate_password_hash(secrets.token_urlsafe(32))


@autenticacao.app_template_global()
def token_formulario():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


@autenticacao.before_request
def validar_formulario():
    recebido = request.form.get("csrf", "")
    esperado = session.get("csrf")
    if not esperado or not secrets.compare_digest(recebido.encode(), esperado.encode()):
        flash("O formulário expirou. Tente novamente nesta página atualizada.")
        return pagina_conta()


def pagina_conta():
    return redirect(url_for("pagina", path="Telas/login_page.html"), code=303)


@autenticacao.post("/api/login")
def entrar():
    nome_usuario = request.form.get("nome_usuario", "").strip()
    senha = request.form.get("senha", "")
    if not nome_usuario or len(nome_usuario) > 254 or not senha or len(senha) > 1024:
        flash("Confira o nome de usuário e a senha.")
        return pagina_conta()

    try:
        with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, nome_usuario, senha_hash FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
            usuario = cursor.fetchone()
    except (ErroBanco, ValueError):
        flash("Não foi possível acessar as contas agora. Tente novamente em instantes.")
        return pagina_conta()

    try:
        valida = check_password_hash(usuario["senha_hash"] if usuario else HASH_AUSENTE, senha)
    except ValueError:
        valida = False
    if not valida or not usuario:
        flash("Usuário ou senha incorretos.")
        return pagina_conta()

    session.clear()
    session.update(usuario_id=usuario["id"], nome=usuario["nome_usuario"])
    return redirect(url_for("pagina", path="index.html"), code=303)


@autenticacao.post("/api/logout")
def sair():
    session.clear()
    return pagina_conta()


@autenticacao.post("/api/cadastro")
def cadastrar():
    usuario = request.form.get("nome_usuario", "").strip()
    senha = request.form.get("senha", "")
    if not (1 <= len(usuario) <= 254
            and 1 <= len(senha) <= 1024) or senha != request.form.get("confirmacao"):
        flash("Preencha os campos e confira a confirmação da senha.")
        return pagina_conta()
    try:
        with conectar_banco() as banco, banco.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios (nome, nome_usuario, senha_hash) VALUES (%s, %s, %s)",
                           ("", usuario, generate_password_hash(senha)))
            banco.commit()
    except IntegrityError:
        flash("Esse nome de usuário já está em uso.")
        return pagina_conta()
    except (ErroBanco, ValueError):
        flash("Não foi possível criar a conta agora. Tente novamente.")
        return pagina_conta()
    flash("Conta criada. Entre com seu usuário e senha.")
    return pagina_conta()


@autenticacao.post("/api/conta/usuario")
def alterar_usuario():
    if not session.get("usuario_id"):
        flash("Entre na sua conta para alterar o usuário.")
        return pagina_conta()
    usuario = request.form.get("nome_usuario", "").strip()
    senha = request.form.get("senha", "")
    if not (1 <= len(usuario) <= 254 and 1 <= len(senha) <= 1024):
        flash("Informe o novo usuário e sua senha atual.")
        return pagina_conta()
    try:
        with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT senha_hash FROM usuarios WHERE id = %s", (session["usuario_id"],))
            conta = cursor.fetchone()
            if not conta or not check_password_hash(conta["senha_hash"], senha):
                flash("Confira sua senha atual.")
                return pagina_conta()
            cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE id = %s",
                           (usuario, session["usuario_id"]))
            banco.commit()
    except IntegrityError:
        flash("Esse nome de usuário já está em uso.")
        return pagina_conta()
    except (ErroBanco, ValueError):
        flash("Não foi possível alterar o usuário agora.")
        return pagina_conta()
    session["nome"] = usuario
    flash("Nome de usuário atualizado.")
    return pagina_conta()
