import sqlalchemy
from flask import Flask, jsonify, request
from sqlalchemy import select
from models import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

# POST recebe a informação
# GET mostra a informação
# PUT atualiza a informação

@app.route('/cadastro_livros', methods=['POST'])
def cadastrar_livros_novos():

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

    db_session = local_session()
    try:
        dados = request.get_json()
        # cadastrar o livro e colocar as informaçoes:
        form_cadastro_livro = Livros(
            titulo=str(dados['titulo']),
            autor=str(dados['autor']),
            ISBN=int(dados['ISBN']),
            resumo=str(dados['resumo'])
        )


        form_cadastro_livro.save(db_session)
        # mensagem que aparece quando o livro é cadastrado
        return jsonify({
            'Mensagem': 'Livro cadastrado!',
            'Titulo': form_cadastro_livro.titulo,
            'Autor': form_cadastro_livro.autor,
            'ISBN': form_cadastro_livro.ISBN,
            'Resumo': form_cadastro_livro.resumo
        })


    except ValueError:
        # caso ocorra algum erro cai nessa mensagem
        return jsonify({
            'erro':'cadastro inválido!'
        })


@app.route('/cadastro_usuario', methods=['POST'])
def cadastrar_novos_usuarios():
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
    db_session = local_session()
    try:
        dados = request.get_json()
        # cadastro de usucario com as informaçoes
        # form_cadastro_usuario = Usuarios(
        #     nome=str(dados['nome']),
        #     CPF=str(dados['CPF']),
        #     endereco=str(dados['endereco'])
        # )
        nome = dados['nome']
        CPF = dados['CPF']
        endereco = dados['endereco']

        novo_usuario = Usuarios(nome=nome,CPF=CPF, endereco=endereco)
        novo_usuario.save(db_session)
        return jsonify({
            'Mensagem': 'Usuário cadastrado!',
            'Nome': novo_usuario.nome,
            'CPF': novo_usuario.CPF,
            'Endereco': novo_usuario.endereco
        })
    except ValueError:
        return jsonify({
            # caso ocorra algum erro parece a seguinte frase:
            'erro':'cadastro inválido!'
        })

@app.route('/realizacao_emprestimos', methods=['POST'])
def novo_emprestimo():
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

    db_session = local_session()
    try:
        dados = request.get_json()

        emprestimo_novo = Emprestimos(data_de_emprestimo=dados["data_emprestimo"],
                                      data_de_devolucao=dados["data_devolucao"],
                                      livro_emprestado=dados["livro"],
                                      usuario_emprestado=dados["usuario_emprestado"],
                                      id_usuario=dados["id_usuario"],
                                      id_livro=dados["id_livro"])
        emprestimo_novo.save(db_session)
        return jsonify({
            'Mensagem': 'Empréstimo realizado'
        })

    except ValueError:
        return jsonify({
            'erro':'cadastro de usuário inválida!'
        })

@app.route('/livros_emprestados', methods=['GET'])
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
    db_session = local_session()
    try:

        # o GET mostra as informaçoes que tem ou seja ira mostrar os livros emprestados
        # select retorna as informaçoes que estao no banco (tabela emprestimo)
        sql_historico_emprestimo = select(Emprestimos)
        # o scalar retorna mais de um objeto
        resultado_historico_emprestimo = db_session.execute(sql_historico_emprestimo).scalars()
        livros_emprestados = []
        for n in resultado_historico_emprestimo:
            livros_emprestados.append(n.serialize_emprestimo())
        return jsonify({'livros emprestados': livros_emprestados})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    finally:
        db_session.close()

@app.route('/livros', methods=['GET'])
def livros():
    """
        Livros
           ## Endpoint:
            /livros

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

    db_session = local_session()
    try:

        # mostra os livros cadastrados
        # select retorna as informaçoes que estao no banco (tabela livros)
        sql_livros = select(Livros)
        # o scalar retorna mais de um objeto
        resultado_livros = db_session.execute(sql_livros).scalars()
        lista_livros = []
        for n in resultado_livros:
            lista_livros.append(n.serialize_livro())
        return jsonify({'lista_livros': lista_livros})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    finally:
        db_session.close()



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

    db_session = local_session()
    try:

        # mostra os usuarios cadastrados
        # select retorna as informaçoes que estao no banco (tabela usuario)
        sql_usuarios = select(Usuarios)
        # o scalar retorna mais de um objeto
        resultado_usuarios = db_session.execute(sql_usuarios).scalars()
        lista_usuarios = []
        for n in resultado_usuarios:
            lista_usuarios.append(n.serialize_usuario())
        return jsonify({'lista_usuarios': lista_usuarios})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    finally:
        db_session.close()


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
    db_session = local_session()
    try:
        # mostra os emprestimos
        # select retorna as informaçoes que estao no banco (tabela Emprestimos)
        sql_emprestimos = select(Emprestimos)
        resultado_emprestimos = db_session.execute(sql_emprestimos).scalars()
        lista_emprestimos = []
        for n in resultado_emprestimos:
            lista_emprestimos.append(n.serialize_emprestimo())
        return jsonify({'lista_emprestimos' : lista_emprestimos})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400
    finally:
        db_session.close()

@app.route('/atualizar_usuario/<id>', methods=['PUT'])
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
    db_session = local_session()

    try:
        dados = request.get_json()
        usuario = select(Usuarios)
        # fazer a busca do banco, filtrando o id:
        usuario_editado = db_session.execute(usuario.filter_by(id_usuario=id)).scalar()

        if not usuario_editado:
            return jsonify({
                "teste": "Não foi possível encontrar o usuário!"
            })

        if request.method == 'PUT':
            # atualizar e verificar se tem algo nos campos
            if (not dados['nome'] and not dados['CPF']
                    and not dados['endereco']):
                return jsonify({
                    # se tiver nulo retorna :
                    "erro": "Os campos não devem ficar em branco!"
                })

            else:
                # edita o usuario
                CPF = dados['CPF'].strip()
                if usuario_editado.CPF != CPF:
                    # vai verificar se nenhum usuario tem esse cpf
                    # scalar retorna o usuario em forma de objeto
                    CPF_existe = db_session.execute(select(Usuarios).where(Usuarios.CPF == CPF)).scalar()

                    if CPF_existe:
                        return jsonify({
                            "erro": "Este CPF já existe!"
                        })
                # o strip remover espaços em branco no início e no fim de uma string
                usuario_editado.nome = dados['nome']
                usuario_editado.CPF = dados['CPF'].strip()
                usuario_editado.endereco = dados['endereco']

                usuario_editado.save()

                return jsonify({
                    "nome": usuario_editado.nome,
                    "CPF": usuario_editado.CPF,
                    "endereco": usuario_editado.endereco,
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "Esse CPF já foi cadastrado!"
        })


@app.route('/atualizar_livro/<id>', methods=['PUT'])
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
    db_session = local_session()
    try:
        dados = request.get_json()
        # fazer a busca do banco, filtrando o id:
        livro_editado = db_session.execute(select(Livros).where(Livros.id_livro == id)).scalar()
        if not livro_editado:
            return jsonify({
                "erro": "O livro não foi encontrado!"
            })

        if request.method == 'PUT':
            # atualizar e verificar se tem algo nos campos
            if (not dados['titulo'] and not dados['autor']
                    and not dados['ISBN'] and not dados['resumo']):
                return jsonify({
                    # se tiver nulo retorna :
                    "erro": "Os campos não devem ficar em branco!"
                })

            else:
                # o strip remover espaços em branco no início e no fim de uma string
                livro_editado.titulo = dados['titulo']
                livro_editado.autor = dados['autor']
                livro_editado.ISBN = dados['ISBN']
                livro_editado.resumo = dados['resumo']

                livro_editado.save()

                return jsonify({
                    "titulo": livro_editado.titulo,
                    "autor": livro_editado.autor,
                    "ISBN": livro_editado.ISBN,
                    "resumo": livro_editado.resumo
                })

    except sqlalchemy.exc.IntegrityError:
        return jsonify({
            "erro": "O titulo já foi cadastrado!"
        })

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

    db_session = local_session()
    try:


        livro_emprestado = db_session.execute(
            # o id livro do livro tem que ser compativel com o id que esta no emprestimo e no livro
            select(Livros).where(Livros.id_livro == Emprestimos.id_livro).distinct(Livros.ISBN)
        ).scalars()

        id_livro_emprestado = db_session.execute(
            select(Emprestimos.id_livro).distinct(Emprestimos.id_livro)
        ).scalars().all()

        print("livro Emprestados",livro_emprestado)
        print("ids_livro_emprestado",id_livro_emprestado)
        livrostatus = db_session.execute(select(Livros)).scalars()

        print("Todos os livros", livrostatus)

        # cria uma lista vazia
        lista_emprestados = []
        lista_disponiveis = []
        for livro in livro_emprestado:
            lista_emprestados.append(livro.serialize_livro())

        print("Resultados da lista:", lista_emprestados)

        for livro in livrostatus:
            if livro.id_livro not in id_livro_emprestado:
                lista_disponiveis.append(livro.serialize_livro())

        print("Resultados disponiveis", lista_disponiveis)


        return jsonify({
            "Livros emprestados": lista_emprestados,
            "Livros disponiveis": lista_disponiveis

        })

    except ValueError:
        return jsonify({
            "error": "Dados indisponíveis"
        })


if __name__ == '__main__':
    app.run(debug=True)