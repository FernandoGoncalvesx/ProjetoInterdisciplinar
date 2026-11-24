import secrets

from flask import Blueprint, flash, redirect, request, session, url_for, render_template
from mysql.connector import Error as ErroBanco, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.usuario import buscar_por_nome, criar_usuario, alterar_nome

autenticacao = Blueprint("autenticacao", __name__)
HASH_AUSENTE = generate_password_hash(secrets.token_urlsafe(32))


@autenticacao.app_template_global()
def token_formulario():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


@autenticacao.before_request
def validar_formulario():
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    recebido = request.form.get("csrf", "")
    esperado = session.get("csrf")
    if not esperado or not secrets.compare_digest(recebido.encode(), esperado.encode()):
        flash("O formulário expirou. Tente novamente nesta página atualizada.")
        return pagina_conta()


def pagina_conta():
    return redirect(url_for("autenticacao.pagina"), code=303)


@autenticacao.post("/api/login")
def entrar():
    nome_usuario = request.form.get("nome_usuario", "").strip()
    senha = request.form.get("senha", "")
    if not nome_usuario or len(nome_usuario) > 254 or not senha or len(senha) > 1024:
        flash("Confira o nome de usuário e a senha.")
        return pagina_conta()

    try:
        usuario = buscar_por_nome(nome_usuario)
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
    return redirect(url_for("inicio.pagina"), code=303)


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
        criar_usuario(usuario, senha)
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
        if not alterar_nome(session["usuario_id"], usuario, senha):
            flash("Confira sua senha atual.")
            return pagina_conta()
    except IntegrityError:
        flash("Esse nome de usuário já está em uso.")
        return pagina_conta()
    except (ErroBanco, ValueError):
        flash("Não foi possível alterar o usuário agora.")
        return pagina_conta()
    session["nome"] = usuario
    flash("Nome de usuário atualizado.")
    return pagina_conta()


@autenticacao.get("/Telas/login_page.html")
def pagina():
    return render_template("paginas/login_page.html", pagina="Telas/login_page.html")
