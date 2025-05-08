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

    try:
        # cadastrar o livro e colocar as informaçoes:
        form_cadastro_livro = Livros(
            titulo=str(request.form['titulo']),
            autor=str(request.form['autor']),
            ISBN=int(request.form['ISBN']),
            resumo=str(request.form['resumo'])
        )


        form_cadastro_livro.save()
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
    try:
        # cadastro de usucario com as informaçoes
        form_cadastro_usuario = Usuarios(
            nome=str(request.form['nome']),
            CPF=str(request.form['CPF']),
            endereco=str(request.form['endereco'])
        )


        form_cadastro_usuario.save()

        return jsonify({
            # mensagem que aparece quando é cadastrado corretamente
            'Mensagem': 'Usuário cadastrado!',
            'Nome': form_cadastro_usuario.nome,
            'CPF': form_cadastro_usuario.CPF,
            'Endereco': form_cadastro_usuario.endereco,
        })


    except ValueError:
        return jsonify({
            # caso ocorra algum erro parece a seguinte frase:
            'erro':'cadastro inválido!'
        })

@app.route('/realizacao_emprestimos', methods=['POST'])
def novo_emprestimo():

    try:
        # realização de emprestimo com essas informaçoes
        form_cadastro_emprestimo = Emprestimos(
            # O id do livro e do usuario para identificar qm pegou o livro e qual livro
            id_usuario = int(request.form['id_usuario']),
            id_livro = int(request.form['id_livro']),

            data_de_emprestimo = request.form['data_de_emprestimo'],
            data_de_devolucao = request.form['data_de_devolucao']
        )
        return jsonify({
            'Mensagem': 'Empréstimo realizado',
            'id_usuario': form_cadastro_emprestimo.id_usuario,
            'id_livro': form_cadastro_emprestimo.id_livro,
            'data_de_emprestimo': form_cadastro_emprestimo.data_de_emprestimo,
            'data_de_devolucao': form_cadastro_emprestimo.data_de_devolucao,
        })

    except ValueError:
        return jsonify({
            'erro':'cadastro inválido!'
        })

@app.route('/livros_emprestados', methods=['GET'])
def historico_emprestimo():
    # o GET mostra as informaçoes que tem ou seja ira mostrar os livros emprestados
    # select retorna as informaçoes que estao no banco (tabela emprestimo)
    sql_historico_emprestimo = select(Emprestimos)
    # o scalar retorna mais de um objeto
    resultado_historico_emprestimo = db_session.execute(sql_historico_emprestimo).scalars()
    livros_emprestados = []
    for n in resultado_historico_emprestimo:
        livros_emprestados.append(n.serialize_emprestimo())
    return jsonify({'livros_emprestados': livros_emprestados})


@app.route('/livros', methods=['GET'])
def livros():
    # mostra os livros cadastrados
    # select retorna as informaçoes que estao no banco (tabela livros)
    sql_livros = select(Livros)
    # o scalar retorna mais de um objeto
    resultado_livros = db_session.execute(sql_livros).scalars()
    lista_livros = []
    for n in resultado_livros:
        lista_livros.append(n.serialize_livro())
    return jsonify({'lista_livros': lista_livros})


@app.route('/usuarios', methods=['GET'])
def usuarios():
    # mostra os usuarios cadastrados
    # select retorna as informaçoes que estao no banco (tabela usuario)
    sql_usuarios = select(Usuarios)
    # o scalar retorna mais de um objeto
    resultado_usuarios = db_session.execute(sql_usuarios).scalars()
    lista_usuarios = []
    for n in resultado_usuarios:
        lista_usuarios.append(n.serialize_usuario())
    return jsonify({'lista_usuarios': lista_usuarios})


@app.route('/emprestimos', methods=['GET'])
def emprestimos():
    # mostra os emprestimos
    # select retorna as informaçoes que estao no banco (tabela Emprestimos)
    sql_emprestimos = select(Emprestimos)
    resultado_emprestimos = db_session.execute(sql_emprestimos).scalars()
    lista_emprestimos = []
    for n in resultado_emprestimos:
        lista_emprestimos.append(n.serialize_emprestimo())
    return jsonify({'lista_emprestimos' : lista_emprestimos})


@app.route('/atualizar_usuario/<id>', methods=['PUT'])
def editar_usuario(id):

    try:
        usuario = select(Usuarios)
        # fazer a busca do banco, filtrando o id:
        usuario_editado = db_session.execute(usuario.filter_by(id_usuario=id)).scalar()

        if not usuario_editado:
            return jsonify({
                "teste": "Não foi possível encontrar o usuário!"
            })

        if request.method == 'PUT':
            # atualizar e verificar se tem algo nos campos
            if (not request.form['nome'] and not request.form['CPF']
                    and not request.form['endereco']):
                return jsonify({
                    # se tiver nulo retorna :
                    "erro": "Os campos não devem ficar em branco!"
                })

            else:
                # edita o usuario
                CPF = request.form['CPF'].strip()
                if usuario_editado.CPF != CPF:
                    # vai verificar se nenhum usuario tem esse cpf
                    # scalar retorna o usuario em forma de objeto
                    CPF_existe = db_session.execute(select(Usuarios).where(Usuarios.CPF == CPF)).scalar()

                    if CPF_existe:
                        return jsonify({
                            "erro": "Este CPF já existe!"
                        })
                # o strip remover espaços em branco no início e no fim de uma string
                usuario_editado.nome = request.form['nome']
                usuario_editado.CPF = request.form['CPF'].strip()
                usuario_editado.endereco = request.form['endereco']

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

    try:
        # fazer a busca do banco, filtrando o id:
        livro_editado = db_session.execute(select(Livros).where(Livros.id_livro == id)).scalar()
        if not livro_editado:
            return jsonify({
                "erro": "O livro não foi encontrado!"
            })

        if request.method == 'PUT':
            # atualizar e verificar se tem algo nos campos
            if (not request.form['titulo'] and not request.form['autor']
                    and not request.form['ISBN'] and not request.form['resumo']):
                return jsonify({
                    # se tiver nulo retorna :
                    "erro": "Os campos não devem ficar em branco!"
                })

            else:
                # o strip remover espaços em branco no início e no fim de uma string
                livro_editado.titulo = request.form['titulo']
                livro_editado.autor = request.form['autor']
                livro_editado.ISBN = request.form['ISBN']
                livro_editado.resumo = request.form['resumo']

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




