from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'segredo123'

USUARIOS_FILE = "usuarios.txt"
CHAT_FILE = "chat.txt"


def carregar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    usuarios = []
    for linha in linhas:
        nome, idade, email, senha, instagram = linha.strip().split(";")
        usuarios.append({
            "nome": nome,
            "idade": idade,
            "email": email,
            "senha": senha,
            "instagram": instagram
        })
    return usuarios


def salvar_usuario(nome, idade, email, senha, instagram):
    with open(USUARIOS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nome};{idade};{email};{senha};{instagram}\n")


def usuario_existente(email, instagram):
    with open("usuarios.txt", "r", encoding="utf-8") as f:
        for linha in f:
            dados = linha.strip().split(";")
            if len(dados) < 5:
                continue
            nome_reg, idade_reg, email_reg, senha_reg, insta_reg = dados
            # Bloqueia se email ou Instagram já existe
            if email_reg == email or (instagram and insta_reg == instagram):
                return True
    return False



def salvar_mensagem(usuario, instagram, mensagem):
    with open(CHAT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{usuario} ({instagram}): {mensagem}\n")


def carregar_mensagens():
    if not os.path.exists(CHAT_FILE):
        return []
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


@app.route('/')
def index():
    erro = request.args.get("erro")
    return render_template('index.html', logado=("usuario" in session), erro=erro)


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["email"] == email and u["senha"] == senha:
            session["usuario"] = u["nome"]
            session["instagram"] = u["instagram"]
            return redirect(url_for('usuarios'))

    # Volta para index com erro
    return render_template('index.html', logado=False, erro="Usuário ou senha incorretos!")


@app.route('/logout')
def logout():
    session.pop("usuario", None)
    session.pop("instagram", None)
    return redirect(url_for('index'))


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    email = request.form.get('email')
    senha = request.form.get('senha')
    instagram = request.form.get('instagram') or ""

    # Verifica duplicidade somente email ou Instagram
    if usuario_existente(email, instagram):
        return render_template('cadastro.html', erro="E-mail ou Instagram já cadastrado!")

    # Salva normalmente
    with open("usuarios.txt", "a", encoding="utf-8") as f:
        f.write(f"{nome};{idade};{email};{senha};{instagram}\n")

    session["usuario"] = nome
    session["instagram"] = instagram
    return redirect(url_for('usuarios'))




@app.route('/usuarios')
def usuarios():
    lista = carregar_usuarios()
    logado = "usuario" in session
    return render_template('usuarios.html', usuarios=lista, logado=logado)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if "usuario" not in session:
        return "<h1>Você precisa estar logado para acessar o chat. <a href='/'>Voltar</a></h1>"

    if request.method == "POST":
        mensagem = request.form.get('mensagem')
        if mensagem.strip():
            salvar_mensagem(session["usuario"], session.get("instagram", ""), mensagem)

    mensagens = carregar_mensagens()
    return render_template('chat.html', mensagens=mensagens)


if __name__ == '__main__':
    app.run(debug=True)