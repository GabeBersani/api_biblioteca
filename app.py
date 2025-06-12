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
def livros():
    """
                Realização de emprestimos

                ## Endpoint:
                 /realizacao_emprestimos

                ## Respostas (JSON):
                ```json

                {
                "id_usuario":,
                "id_livro",
                "data_emprestimo",
                "data_emprestimo",
                 }

                ## Erros possíveis (JSON):
                  "Empréstimo realizad"
                 Bad Request***:
                     ```json
                """

    sql_livros = select(Livro)
    resultado_livros = db_session.execute(sql_livros).scalars()
    # Garante que 'id_livro' é incluído na serialização
    lista_livros = [ {**n.serialize_livro(), "id_livro": n.id_livro} for n in resultado_livros]
    return jsonify({'livros': lista_livros})


@app.route('/usuarios', methods=['GET'])
def usuarios():
    """
        Usuarios
           ## Endpoint:
            /usuarios

           ## Respostas (JSON):
           ```json

        {
            "livros":Lista de livros"
        }
        ## Erros possíveis (JSON):
        "cadastro inválido!"
        Bad Request***:
            ```json
    """
    sql_usuarios = select(Usuario)
    resultado_usuarios = db_session.execute(sql_usuarios).scalars()
    # Garante que 'id_usuario' é incluído na serialização
    lista_usuarios = [ {**n.serialize_usuario(), "id_usuario": n.id_usuario} for n in resultado_usuarios]
    return jsonify({'usuarios': lista_usuarios})


@app.route('/emprestimos', methods=['GET'])
def emprestimos():
    """
          emprestimos

          ## Endpoint:
           /emprestimos

          ## Respostas (JSON):
          ```json

          {
               "emprestimos": lista_emprestimos
          }

           ## Erros possíveis (JSON):
           "dados indisponiveis ***400
           Bad Request***:
               ```json
       """
    sql_emprestimos = select(Emprestimo)
    resultado_emprestimos = db_session.execute(sql_emprestimos).scalars()
    # Garante que 'id_emprestimo' é incluído na serialização
    lista_emprestimos = [ {**n.serialize_emprestimo(), "id_emprestimo": n.id_emprestimo} for n in resultado_emprestimos]
    return jsonify({'emprestimos': lista_emprestimos})


@app.route('/novo_livro', methods=['POST'])
def cadastrar_livros():
    """
               Cadastro de Livros

               ## Endpoint:
                /cadastro_livros

               ## Respostas (JSON):
               ```json

               {
                    "titulo",
                    "autor":,
                    "ISBN",
                    "resumo",
                }

               ## Erros possíveis (JSON):
                "cadastro inválido!"
                Bad Request***:
                    ```json
               """
    dados = request.get_json()
    try:
        # Ajuste para aceitar tanto 'isbn' minúsculo quanto 'ISBN' maiúsculo
        isbn_value = dados.get('isbn') or dados.get('ISBN')
        if not all([dados.get('titulo'), dados.get('autor'), isbn_value, dados.get('resumo')]):
            return jsonify({'erro': "Campos não podem ser vazios"}), 400

        novo_livro = Livro(
            titulo=dados['titulo'],
            autor=dados['autor'],
            ISBN=isbn_value,
            resumo=dados['resumo']
        )
        novo_livro.save()
        return (jsonify
                ({**novo_livro.serialize_livro(), "id_livro": novo_livro.id_livro}), 201)
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


@app.route('/novo_usuario', methods=['POST'])
def cadastrar_usuarios():
    """
               Cadastro de usuário

               ## Endpoint:
                /cadastro_usuario

               ## Respostas (JSON):
               ```json

               {
                    "nome",
                    "CPF":,
                    "endereco",
                }

               ## Erros possíveis (JSON):
                "cadastro inválido!"
                Bad Request***:
                    ```json
               """
    try:
        dados = request.get_json()
        if not all([dados.get('nome'), dados.get('cpf'), dados.get('endereco')]):
            return jsonify({'erro': "Campos não podem ser vazios"}), 400

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



@app.route('/realizar_emprestimo', methods=['POST'])
def cadastrar_emprestimo():
    """
               Cadastro de usuário

               ## Endpoint:
                /cadastro_usuario

               ## Respostas (JSON):
               ```json

               {
                    "nome",
                    "CPF":,
                    "endereco",
                }

               ## Erros possíveis (JSON):
                "cadastro inválido!"
                Bad Request***:
                    ```json
               """
    dados = request.get_json()
    try:
        # Usar as chaves consistentes 'id_usuario' e 'id_livro'
        if not all([dados.get('id_usuario'), dados.get('id_livro'), dados.get('data_emprestimo'), dados.get('data_devolucao')]):
            return jsonify({'erro': "Campos obrigatórios estão ausentes"}), 400

        # Verificar se usuário e livro existem
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
        return jsonify({**novo_emprestimo.serialize_emprestimo(), "id_emprestimo": novo_emprestimo.id_emprestimo}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


@app.route('/consulta_historico_emprestimo', methods=['GET'])
def historico_emprestimo():
    """
        Livros
           ## Endpoint:
            /livros_emprestados

           ## Respostas (JSON):
           ```json

        {
            "livros emprestados"
        }
        ## Erros possíveis (JSON):
        "cadastro inválido!"
        Bad Request***:
            ```json
    """
    sql = select(Emprestimo)
    emprestimos = db_session.execute(sql).scalars()
    lista = [ {**e.serialize_emprestimo(), "id_emprestimo": e.id_emprestimo} for e in emprestimos]
    return jsonify({'historico_de_emprestimo': lista})

@app.route('/editar_usuario/<int:id>', methods=['PUT']) # Rota alterada de 'atualizar' para 'editar'
def editar_usuario(id):
    """
                  Atualizar dados do usuario

                  ## Endpoint:
                   /atualizar_usuario/<id>

                   ##Parâmetros:
                   "id" **Id do usuario**

                  ## Respostas (JSON):
                  ```json

                  {
                       "nome":
                       "CPF",
                       "endereco":,
                   }

                  ## Erros possíveis (JSON):
                   "teste": "Não foi possível encontrar o usuário!"
                   "erro": "Os campos não devem ficar em branco!"
                   "erro": "Este CPF já existe!"
                   "erro": "Esse CPF já foi cadastrado!"

                   Bad Request***:
                       ```json
                  """
    dados = request.get_json()
    try:
        usuario = db_session.execute(select(Usuario).where(Usuario.id_usuario == id)).scalar()
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404

        updated = False
        # Mapeamento para garantir que 'cpf' no JSON seja usado para 'CPF' no modelo
        if 'nome' in dados and dados['nome'] is not None:
            usuario.nome = dados['nome']
            updated = True
        if 'cpf' in dados and dados['cpf'] is not None:
            usuario.CPF = dados['cpf'] # Atualiza o campo CPF do modelo
            updated = True
        if 'endereco' in dados and dados['endereco'] is not None:
            usuario.endereco = dados['endereco']
            updated = True

        if updated:
            usuario.save()
        return jsonify({**usuario.serialize_usuario(), "id_usuario": usuario.id_usuario})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/editar_livro/<int:id>', methods=['PUT']) # Rota alterada de 'atualizar' para 'editar'
def editar_livro(id):
    """
                   Atualizar livro.
                   ## Endpoint:
                    /atualizar_livro/<id>

                    ## Parâmetro:
                    "id" **Id do livro**

                   ## Respostas (JSON):
                   ```json

                   {
                        "titulo":
                        "autor",
                        "ISBN":,
                        "resumo",
                    }

                   ## Erros possíveis (JSON):
                     "erro": "Os campos não devem ficar em branco!"
                    Bad Request***:
                        ```json
                   """
    dados = request.get_json()
    try:
        livro = db_session.execute(select(Livro).where(Livro.id_livro == id)).scalar()
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404

        updated = False
        # Mapeamento para garantir que 'isbn' no JSON seja usado para 'ISBN' no modelo
        if 'titulo' in dados and dados['titulo'] is not None:
            livro.titulo = dados['titulo']
            updated = True
        if 'autor' in dados and dados['autor'] is not None:
            livro.autor = dados['autor']
            updated = True
        if 'isbn' in dados and dados['isbn'] is not None: # Espera 'isbn' minúsculo do frontend
            livro.ISBN = dados['isbn']
            updated = True
        if 'resumo' in dados and dados['resumo'] is not None:
            livro.resumo = dados['resumo']
            updated = True

        if updated:
            livro.save()
        return jsonify({**livro.serialize_livro(), "id_livro": livro.id_livro})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/livro_status', methods=['GET'])
def livro_status():
    """
                   livro status .

                    ## Endpoint:
                     /livro_status
                    ## Respostas (JSON):
                    ```json
                    {
                         "livros emprestados":
                         "livros disponiveis",
                     }

                     ## Erros possíveis (JSON):
                    "error": "Dados indisponíveis"
                     Bad Request***:
                         ```json
                     """
    try:
        # Obter IDs dos livros emprestados
        emprestimos_livro_ids = {e.id_livro for e in db_session.execute(select(Emprestimo)).scalars()}
        todos_livros = db_session.execute(select(Livro)).scalars().all() # .all() para carregar antes de iterar

        emprestados = []
        disponiveis = []

        for livro in todos_livros:
            if livro.id_livro in emprestimos_livro_ids:
                emprestados.append({**livro.serialize_livro(), "id_livro": livro.id_livro})
            else:
                disponiveis.append({**livro.serialize_livro(), "id_livro": livro.id_livro})

        return jsonify({
            "livros_emprestados": emprestados,
            "livros_disponiveis": disponiveis
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
