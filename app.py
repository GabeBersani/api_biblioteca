import sqlalchemy
from flask import Flask, jsonify, request
from sqlalchemy import select
from models import Livro, Usuario, Emprestimo, db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/livros', methods=['GET'])
def get_livros():
    """
    Retorna uma lista de todos os livros cadastrados.

    Endpoint:
    /livros

    Respostas (JSON):
    ```json
    {
        "livros": [
            {
                "id_livro": 1,
                "titulo": "O Senhor dos Anéis",
                "autor": " Gabriele",
                "ISBN": "9788533302273",
                "resumo": "Uma aventura épica..."
            }
        ]
    }
    ```
    Erros possíveis (JSON):
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    """
    try:
        sql_livros = select(Livro)
        resultado_livros = db_session.execute(sql_livros).scalars()
        lista_livros = []
        for livro in resultado_livros:
            livro_data = livro.serialize_livro()
            livro_data["id_livro"] = livro.id_livro
            lista_livros.append(livro_data)
        return jsonify({'livros': lista_livros})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/novo_livro', methods=['POST'])
def cadastrar_livro():
    """
    Cadastra um novo livro no sistema.

    Endpoint:
    /novo_livro

    Corpo da Requisição (JSON):
    ```json
    {
        "titulo": "Nome do Livro",
        "autor": "Nome do Autor",
        "isbn": "123-456-789-0",
        "resumo": "Um breve resumo do livro."
    }
    ```

    Respostas (JSON):
    ```json
    {
        "id_livro": 1,
        "titulo": "Nome do Livro",
        "autor": "Nome do Autor",
        "ISBN": "123-456-789-0",
        "resumo": "Um breve resumo do livro."
    }
    ```
    Status: 201 Created

    Erros possíveis (JSON):
    ```json
    {
        "erro": "Campos não podem ser vazios"
    }
    ```
    Status: 400 Bad Request
    """
    dados = request.get_json()
    try:
        isbn_value = dados.get('isbn') or dados.get('ISBN')
        if not all([dados.get('titulo'), dados.get('autor'), isbn_value, dados.get('resumo')]):
            return jsonify({'erro': "Campos obrigatórios (titulo, autor, ISBN/isbn, resumo) não podem ser vazios"}), 400

        novo_livro = Livro(
            titulo=dados['titulo'],
            autor=dados['autor'],
            ISBN=isbn_value,
            resumo=dados['resumo']
        )
        novo_livro.save()
        livro_response = novo_livro.serialize_livro()
        livro_response["id_livro"] = novo_livro.id_livro
        return jsonify(livro_response), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/editar_livro/<int:id>', methods=['PUT'])
def editar_livro(id):
    """
    Atualiza os dados de um livro existente.

    Endpoint:
    /editar_livro/<id>

    Parâmetros:
    "id": ID do livro a ser atualizado.

    Corpo da Requisição (JSON):
    ```json
    {
        "titulo": "Novo Título",
        "autor": "Novo Autor",
        "isbn": "987-654-321-0",
        "resumo": "Novo resumo."
    }
    ```
    (Envie apenas os campos que deseja atualizar)

    Respostas (JSON):
    ```json
    {
        "id_livro": 1,
        "titulo": "novo Título",
        "autor": "novo Autor",
        "ISBN": "11111111111",
        "resumo": "Novo resumo."
    }
    ```
    Status: 200

    Erros possíveis (JSON):
    ```json
    {
        "erro": "Livro não encontrado"
    }
    ```
    Status: 404 Not Found
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    Status: 400 Bad Request
    """
    dados = request.get_json()
    try:
        livro = db_session.execute(select(Livro).where(Livro.id_livro == id)).scalar()
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404

        updated = False
        if 'titulo' in dados and dados['titulo'] is not None:
            livro.titulo = dados['titulo']
            updated = True
        if 'autor' in dados and dados['autor'] is not None:
            livro.autor = dados['autor']
            updated = True
        if 'isbn' in dados and dados['isbn'] is not None:
            livro.ISBN = dados['isbn']
            updated = True
        if 'resumo' in dados and dados['resumo'] is not None:
            livro.resumo = dados['resumo']
            updated = True

        if updated:
            livro.save()
        livro_response = livro.serialize_livro()
        livro_response["id_livro"] = livro.id_livro
        return jsonify(livro_response)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/livro_status', methods=['GET'])
def livro_status():
    """
    Retorna o status dos livros, separando-os entre emprestados e disponíveis.

    Endpoint:
    /livro_status

    Respostas (JSON):
    ```json
    {
        "livros_emprestados": [
            {
                "id_livro": 1,
                "titulo": "Livro Emprestado 1",
                "autor": "Autor 1",
                "ISBN": "123-456",
                "resumo": "Resumo 1"
            }
        ],
        "livros_disponiveis": [
            {
                "id_livro": 2,
                "titulo": "Livro Disponível 1",
                "autor": "Autor 2",
                "ISBN": "789-012",
                "resumo": "Resumo 2"
            }
        ]
    }
    ```

    Erros possíveis (JSON):
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    Status: 400 Bad Request
    """
    try:
        emprestimos_livro_ids = {e.id_livro for e in db_session.execute(select(Emprestimo)).scalars()}
        todos_livros = db_session.execute(select(Livro)).scalars().all()

        emprestados = []
        disponiveis = []

        for livro in todos_livros:
            livro_data = livro.serialize_livro()
            livro_data["id_livro"] = livro.id_livro
            if livro.id_livro in emprestimos_livro_ids:
                emprestados.append(livro_data)
            else:
                disponiveis.append(livro_data)

        return jsonify({
            "livros_emprestados": emprestados,
            "livros_disponiveis": disponiveis
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 400



@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    """
    Retorna uma lista de todos os usuários cadastrados.

    Endpoint:
    /usuarios

    Respostas (JSON):
    ```json
    {
        "usuarios": [
            {
                "id_usuario": 1,
                "nome": "João Silva",
                "CPF": "123.456.789-00",
                "endereco": "Rua A, 123"
            }
        ]
    }
    ```
    Erros possíveis (JSON):
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    """
    try:
        sql_usuarios = select(Usuario)
        resultado_usuarios = db_session.execute(sql_usuarios).scalars()
        lista_usuarios = []
        for usuario in resultado_usuarios:
            usuario_data = usuario.serialize_usuario()
            usuario_data["id_usuario"] = usuario.id_usuario
            lista_usuarios.append(usuario_data)
        return jsonify({'usuarios': lista_usuarios})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/novo_usuario', methods=['POST'])
def cadastrar_usuario():
    """
    Cadastra um novo usuário no sistema.

    Endpoint:
    /novo_usuario

    Corpo da Requisição (JSON):
    ```json
    {
        "nome": "Maria Souza",
        "cpf": "987.654.321-11",
        "endereco": "Avenida B, 456"
    }
    ```

    Respostas (JSON):
    ```json
    {
        "status": true,
        "mensagem": "usuario cadastrado com sucesso!"
    }
    ```
    Status: 201 Created

    Erros possíveis (JSON):
    ```json
    {
        "status": false,
        "erro": "Campos não podem ser vazios"
    }
    ```
    Status: 400 Bad Request
    """
    try:
        dados = request.get_json()
        if not all([dados.get('nome'), dados.get('cpf'), dados.get('endereco')]):
            return jsonify({'status': False, 'erro': "Campos obrigatórios (nome, cpf, endereco) não podem ser vazios"}), 400

        novo_usuario = Usuario(
            nome=dados['nome'],
            CPF=dados['cpf'],
            endereco=dados['endereco']
        )
        novo_usuario.save()
        return jsonify({
            "status": True,
            "mensagem": "usuario cadastrado com sucesso!"
        }), 201
    except Exception as e:
        return jsonify({
            "status": False,
            "erro": str(e)
        }), 400

@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    """
    Atualiza os dados de um usuário existente.

    Endpoint:
    /editar_usuario/<id>

    Parâmetros:
    "id": ID do usuário a ser atualizado.

    Corpo da Requisição (JSON):
    ```json
    {
        "nome": "Novo Nome do Usuário",
        "cpf": "111.222.333-44",
        "endereco": "Nova Rua, 789"
    }
    ```
    (Envie apenas os campos que deseja atualizar)

    Respostas (JSON):
    ```json
    {
        "id_usuario": 1,
        "nome": "Novo Nome do Usuário",
        "CPF": "111.222.333-44",
        "endereco": "Nova Rua, 789"
    }
    ```
    Status: 200 OK

    Erros possíveis (JSON):
    ```json
    {
        "erro": "Usuário não encontrado"
    }
    ```
    Status: 404 Not Found
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    Status: 400 Bad Request
    """
    dados = request.get_json()
    try:
        usuario = db_session.execute(select(Usuario).where(Usuario.id_usuario == id)).scalar()
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        updated = False
        if 'nome' in dados and dados['nome'] is not None:
            usuario.nome = dados['nome']
            updated = True
        if 'cpf' in dados and dados['cpf'] is not None:
            usuario.CPF = dados['cpf']
            updated = True
        if 'endereco' in dados and dados['endereco'] is not None:
            usuario.endereco = dados['endereco']
            updated = True

        if updated:
            usuario.save()
        usuario_response = usuario.serialize_usuario()
        usuario_response["id_usuario"] = usuario.id_usuario
        return jsonify(usuario_response)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


@app.route('/emprestimos', methods=['GET'])
def get_emprestimos():
    """
    Retorna uma lista de todos os empréstimos registrados.

    Endpoint:
    /emprestimos

    Respostas (JSON):
    ```json
    {
        "emprestimos": [
            {
                "id_emprestimo": 1,
                "id_usuario": 1,
                "id_livro": 1,
                "data_emprestimo": "2024-01-01",
                "data_devolucao": "2024-01-15"
            }
        ]
    }
    ```
    Erros possíveis (JSON):
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    """
    try:
        sql_emprestimos = select(Emprestimo)
        resultado_emprestimos = db_session.execute(sql_emprestimos).scalars()
        lista_emprestimos = []
        for emprestimo in resultado_emprestimos:
            emprestimo_data = emprestimo.serialize_emprestimo()
            emprestimo_data["id_emprestimo"] = emprestimo.id_emprestimo
            lista_emprestimos.append(emprestimo_data)
        return jsonify({'emprestimos': lista_emprestimos})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/realizar_emprestimo', methods=['POST'])
def cadastrar_emprestimo():
    """
    Realiza um novo empréstimo de livro para um usuário.

    Endpoint:
    /realizar_emprestimo

    Corpo da Requisição (JSON):
    ```json
    {
        "id_usuario": 1,
        "id_livro": 2,
        "data_emprestimo": "YYYY-MM-DD",
        "data_devolucao": "YYYY-MM-DD"
    }
    ```

    Respostas (JSON):
    ```json
    {
        "id_emprestimo": 1,
        "id_usuario": 1,
        "id_livro": 2,
        "data_emprestimo": "YYYY-MM-DD",
        "data_devolucao": "YYYY-MM-DD"
    }
    ```
    Status: 201 Created

    Erros possíveis (JSON):
    ```json
    {
        "erro": "Campos obrigatórios estão ausentes"
    }
    ```
    Status: 400 Bad Request
    ```json
    {
        "erro": "Usuário não encontrado"
    }
    ```
    Status: 404 Not Found
    ```json
    {
        "erro": "Livro não encontrado"
    }
    ```
    Status: 404 Not Found
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    Status: 400 Bad Request
    """
    dados = request.get_json()
    try:
        if not all([dados.get('id_usuario'), dados.get('id_livro'), dados.get('data_emprestimo'), dados.get('data_devolucao')]):
            return jsonify({'erro': "Campos obrigatórios (id_usuario, id_livro, data_emprestimo, data_devolucao) estão ausentes"}), 400

        usuario_existente = db_session.execute(select(Usuario).where(Usuario.id_usuario == dados['id_usuario'])).scalar()
        livro_existente = db_session.execute(select(Livro).where(Livro.id_livro == dados['id_livro'])).scalar()

        if not usuario_existente:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        if not livro_existente:
            return jsonify({'erro': 'Livro não encontrado'}), 404

        novo_emprestimo = Emprestimo(
            id_usuario=dados['id_usuario'],
            id_livro=dados['id_livro'],
            data_emprestimo=dados['data_emprestimo'],
            data_devolucao=dados['data_devolucao']
        )
        novo_emprestimo.save()
        emprestimo_response = novo_emprestimo.serialize_emprestimo()
        emprestimo_response["id_emprestimo"] = novo_emprestimo.id_emprestimo
        return jsonify(emprestimo_response), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/consulta_historico_emprestimo', methods=['GET'])
def historico_emprestimo():
    """
    Retorna o histórico de todos os empréstimos.

    Endpoint:
    /consulta_historico_emprestimo

    Respostas (JSON):
    ```json
    {
        "historico_de_emprestimo": [
            {
                "id_emprestimo": 1,
                "id_usuario": 1,
                "id_livro": 1,
                "data_emprestimo": "2024-01-01",
                "data_devolucao": "2024-01-15"
            }
        ]
    }
    ```
    Erros possíveis (JSON):
    ```json
    {
        "erro": "Mensagem de erro"
    }
    ```
    """
    try:
        sql = select(Emprestimo)
        emprestimos = db_session.execute(sql).scalars()
        lista = []
        for e in emprestimos:
            emprestimo_data = e.serialize_emprestimo()
            emprestimo_data["id_emprestimo"] = e.id_emprestimo
            lista.append(emprestimo_data)
        return jsonify({'historico_de_emprestimo': lista})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)