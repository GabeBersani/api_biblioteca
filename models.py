from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base

engine = create_engine('sqlite:///biblioteca.sqlite3')

#db_session = scoped_session(sessionmaker(bind=engine))
local_session = sessionmaker(bind=engine)

Base = declarative_base()
#Base.query = db_session.query_property()

class Usuarios(Base):
    __tablename__ = "Usuario"
    id_usuario = Column(Integer,primary_key=True, autoincrement=True)
    nome = Column(String(40), nullable=False, index=True)
    CPF = Column(String(11), nullable=False, index=True, unique=True)
    endereco = Column(String(50), nullable=False, index=True)

    def __repr__(self):
        return '<Produto: {} {} {} {}'.format(self.id_usuario, self.nome, self.CPF, self.endereco)

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            raise
    #
    # def delete(self):
    #     db_session.delete(self)
    #     db_session.commit()

    def serialize_usuario(self):
        dados_usuario = {
            "Nome": self.nome,
            "CPF": self.CPF,
            "Endereço": self.endereco
        }
        return dados_usuario


class Livros(Base):
    __tablename__ = "Livro"
    # id unico do livro
    id_livro = Column(Integer, primary_key=True)
    titulo = Column(String(40), nullable=False, index=True, unique=True)
    autor = Column(String(30), nullable=False, index=True)
    ISBN = Column(Integer, nullable=False, index=True)
    resumo = Column(String(200), nullable=False, index=True)

    def __repr__(self):
        return '<Livro: {} {} {} {} {}'.format(self.id_livro, self.titulo, self.autor, self.ISBN, self.resumo)

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            raise e
    #
    # def delete(self):
    #     db_session.delete(self)
    #     db_session.commit()

    def serialize_livro(self):
        dados_livro = {
            "Título": self.titulo,
            "Autor": self.autor,
            "ISBN": self.ISBN,
            "Resumo": self.resumo
        }
        return dados_livro


class Emprestimos(Base):
    __tablename__ = "Emprestimo"
    id_emprestimo = Column(Integer, primary_key=True, autoincrement=True)
    data_emprestimo = Column(String(10), nullable=False, index=True)
    data_devolucao = Column(String(10), nullable=False, index=True)
    livro_emprestado = Column(String(50), nullable=False, index=True)
    usuario_emprestado = Column(String(50), nullable=False, index=True)
    id_usuario = Column(Integer, ForeignKey('Usuario.id_usuario'))
    usuario = relationship('Usuarios')
    id_livro = Column(Integer, ForeignKey('Livro.id_livro'))
    livro = relationship('Livros')

    def __repr__(self):
        return '<Venda: {} {} {} {} {} '.format(self.id_emprestimo, self.data_emprestimo, self.data_devolucao,
                                                self.livro_emprestado, self.usuario_emprestado)

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            raise e

    # def delete(self):
    #     db_session.delete(self)
    #     db_session.commit()

    def serialize_emprestimo(self):
        dados_emprestimo = {
            "Data de empréstimo": self.data_emprestimo,
            "Data de devolução": self.data_devolucao,
            "Livro emprestado": self.livro_emprestado,
            "Usúario emprestado": self.usuario_emprestado,
            'Usúario': self.id_usuario,
            'Livro': self.id_livro,
        }
        return dados_emprestimo


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()