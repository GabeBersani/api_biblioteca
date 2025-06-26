from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DateTime, Float
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine('sqlite:///base_biblioteca.sqlite3')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    senha_hash = Column(String, nullable=False) #senha com proteção
    papel = Column(String, nullable=False) #cargo das pessoas

    def set_senha_hash(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def serialize(self):
        dados = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'papel': self.papel,
        }
        return dados


class Livro(Base):
    __tablename__ = 'LIVROS'
    id_livro = Column(Integer, primary_key=True)
    titulo = Column(String(40), nullable=False, index=True, unique=True)
    autor = Column(String(30), nullable=False, index=True)
    ISBN = Column(Integer, nullable=False, index=True)
    resumo = Column(String(200), nullable=False, index=True)

    def __repr__(self):
        return '<Livro: {} {} {} {} {}'.format(self.id_livro, self.titulo, self.autor, self.ISBN, self.resumo)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def update(self, titulo=None, autor=None, ISBN=None, resumo=None):
        if titulo:
            self.titulo = titulo
        if autor:
            self.autor = autor
        if ISBN:
            self.ISBN = ISBN
        if resumo:
            self.resumo = resumo
        db_session.commit()

    def serialize_livro(self):
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.ISBN,
            "resumo": self.resumo
        }

class Usuario(Base):
    __tablename__ = 'USUARIOS'
    id_usuario = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    CPF = Column(String(11), nullable=False, index=True, unique=True)
    endereco = Column(String(50), nullable=False, index=True)

    def __repr__(self):
        return '<Usuario: {} {} {} {}'.format(self.id_usuario, self.nome, self.CPF, self.endereco)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def update(self, nome=None, CPF=None, endereco=None):
        if nome:
            self.nome = nome
        if CPF:
            self.CPF = CPF
        if endereco:
            self.endereco = endereco
        db_session.commit()

    def serialize_usuario(self):
        return {
            "nome": self.nome,
            "cpf": self.CPF,
            "endereco": self.endereco
        }

class Emprestimo(Base):
    __tablename__ = 'EMPRÉSTIMOS'
    id_emprestimo = Column(Integer, primary_key=True)
    data_emprestimo = Column(String(8), nullable=False, index=True)
    data_devolucao = Column(String(8), nullable=False, index=True)

    id_usuario = Column(Integer, ForeignKey('USUARIOS.id_usuario'))
    usuario = relationship('Usuario')
    id_livro = Column(Integer, ForeignKey('LIVROS.id_livro'))
    livro = relationship('Livro')

    def __repr__(self):
        return '<Emprestimo: {} {} {}>'.format(self.id_emprestimo, self.data_emprestimo, self.data_devolucao)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def update(self, data_emprestimo=None, data_devolucao=None):
        if data_emprestimo:
            self.data_emprestimo = data_emprestimo
        if data_devolucao:
            self.data_devolucao = data_devolucao
        db_session.commit()

    def serialize_emprestimo(self):
        return {
            "data de emprestimo": self.data_emprestimo,
            "data de devolucao": self.data_devolucao,
            'usuario': self.id_usuario,
            'livro': self.id_livro,
        }

    class UsuarioGeral(Base):
        __tablename__ = 'usuarios_exemplo'
        id = Column(Integer, primary_key=True)
        nome = Column(String, nullable=False)
        email = Column(String, nullable=False)
        senha_hash = Column(String, nullable=False)
        papel = Column(String, nullable=False)

        def set_senha_hash(self, senha):
            self.senha_hash = generate_password_hash(senha)

        def check_password_hash(self, senha):
            return check_password_hash(self.senha_hash, senha)

        def serialize(self):
            dados = {
                'id': self.id,
                'nome': self.nome,
                'email': self.email,
                'papel': self.papel,  # papel não é obrigatorio
            }
            return dados

    class NotasExemplo(Base):
        __tablename__ = 'notas_exemplo'
        id = Column(Integer, primary_key=True)
        conteudo = Column(String, nullable=False)
        # user_id = Column(Integer, ForeignKey('usuarios_exemplo.id')) # Poderia ter para associar

    Base.metadata.create_all(engine)  # Cria as tabelas

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()

