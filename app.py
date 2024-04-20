from urllib.parse import unquote
from flask import Flask, request, jsonify, redirect
from models import db, Quarto, Reserva, Cliente
from flask_cors import CORS
from schemas import *
from pydantic import ValidationError
from datetime import datetime
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI, Info, Tag




info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy
db.init_app(app)
# Criação das tabelas
with app.app_context():
    db.create_all()


# Definições de rota
quarto_tag = Tag(name='Quarto', description='Cadastro, consulta, edição e deleção de um quarto')
reserva_tag = Tag(name='Reserva', description='Cadastro,consulta, edição e deleção de uma reserva.')
cliente_tag = Tag(name='Cliente', description='Cadastro, consulta, edição e deleção de um cliente')
# Rota principal
@app.get('/')
def home():
        return redirect('/openapi')

# Rota para buscar todos os quartos
@app.get('/quartos', tags=[quarto_tag], responses={"200": QuartoViewSchema})
def get_todos_quartos():
    """Lista todos os Quartos da base de dados

    Retorna uma representação do Quarto.
    """
    todos_quartos = Quarto.query.all()
    return jsonify([quarto.serialize() for quarto in todos_quartos])

# Rota para buscar quartos vagos
@app.get('/quartos_vagos', tags=[quarto_tag], responses={"200": QuartoViewSchema})
def get_quartos_vagos():
    """Lista todos os Quartos vagos da base de dados

    Retorna uma representação do Quarto.
    """
    quartos_vagos = Quarto.query.filter_by(vago=True).all()
    return jsonify([quarto.serialize() for quarto in quartos_vagos])


# Rota para editar um quarto existente
@app.put('/quartos', tags=[quarto_tag], responses={"200": QuartoEditSchema, "409": ErrorSchema, "400": ErrorSchema})
def editar_quarto(query: QuartoBuscaPorIDSchema, form: QuartoEditSchema):
    """Edita um Quarto existente na base de dados

    Retorna uma confirmação alteração.
    """
    print(form)
    quarto_id = int(query.id)

    quarto = {
        'capacidade_maxima': form.capacidade_maxima,
        'valor_diaria': form.valor_diaria,
    }

    db.session.query(Quarto).filter(Quarto.id == quarto_id).update(quarto)
    db.session.commit()

    return jsonify({"message": "Informações do quarto atualizadas com sucesso"}), 200

# Rota para criar um novo quarto
@app.post('/quartos', tags=[quarto_tag], responses={"200": QuartoCreateSchema,"409": ErrorSchema, "400": ErrorSchema})
def add_quarto(form: QuartoCreateSchema):
    """Adiciona um novo Quarto à base de dados

    Retorna uma confirmação de cadastramento.
    """
    print(form)
    quarto = Quarto(  
        numero = form.numero,
        capacidade_maxima = form.capacidade_maxima,
        valor_diaria = form.valor_diaria,
        vago = form.vago,
    )
    try:
        db.session.add(quarto)
        db.session.commit()
        return jsonify({'message': 'Quarto criado com sucesso!'}), 201

    except Exception as e:
        error_msg = "Não foi possível salvar novo quarto :/"
        return {"message": error_msg}, 400

# Rota para deletar um quarto
@app.delete('/quartos', tags=[quarto_tag], responses={"200": QuartoDelSchema, "404": ErrorSchema})
def excluir_quarto(query: QuartoBuscaPorIDSchema):
    """Deleta um Quarto a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    quarto_id = int(query.id)
    quarto = Quarto.query.get(quarto_id)

    if not quarto:
        return jsonify({"error": "Quarto não encontrado"}), 404

    if not quarto.vago:
        return jsonify({"error": "O quarto está ocupado. Favor fazer o checkout antes de excluir"}), 409

    # Se o quarto estiver vago, podemos prosseguir com a exclusão
    db.session.delete(quarto)
    db.session.commit()

    return jsonify({"message": "Quarto removido com sucesso"}), 200

# Rota para cadastrar um novo cliente
@app.post('/clientes', tags=[cliente_tag], responses={"200": ClienteCreateSchema,"409": ErrorSchema, "400": ErrorSchema})
def add_cliente(form: ClienteCreateSchema):
    """Adiciona um novo Cliente à base de dados

    Retorna uma confirmação de cadastramento.
    """
    print(form)
    cliente = Cliente(  
        nome = form.nome,
        sobrenome = form.sobrenome,
        celular = form.celular,
        email = form.email,

    )
    try:
        db.session.add(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente criado com sucesso!'}), 201

    except Exception as e:
        error_msg = "Não foi possível salvar novo cliente :/"
        return {"message": error_msg}, 400

# Rota para buscar todos os clientes
@app.get('/clientes',tags=[cliente_tag], responses={"200": ClienteViewSchema})
def get_clientes():
    """Lista todos os Clientes da base de dados

    Retorna uma representação do Cliente.
    """
    clientes = Cliente.query.all()
    return jsonify([cliente.serialize() for cliente in clientes])

# Rota para editar um cliente existente
@app.put('/clientes/', tags=[cliente_tag], responses={"200": ClienteEditSchema, "409": ErrorSchema, "400": ErrorSchema})
def editar_cliente(query: ClienteBuscaPorIDSchema, form: ClienteEditSchema):
    """Edita um Cliente existente na base de dados

    Retorna uma confirmação alteração.
    """
    print(form)
    cliente_id = int(query.id)
    
    cliente = {
        'nome': form.nome,
        'sobrenome': form.sobrenome,
        'celular': form.celular,
        'email': form.email,
    }
   
    db.session.query(Cliente).filter(Cliente.id == cliente_id).update(cliente)
    db.session.commit()

    return jsonify({"message": "Informações do cliente atualizadas com sucesso"}), 200

# Rota para excluir um cliente existente
@app.delete('/clientes', tags=[cliente_tag], responses={"200": ClienteDelSchema, "404": ErrorSchema})
def excluir_cliente(query: ClienteBuscaPorIDSchema):
    """Deleta um Cliente a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    cliente_id = int(query.id)
    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        return jsonify({"error": "Cliente não encontrado"}), 404

    # Verificar se o cliente está associado a alguma reserva
    if cliente.reservas:
        return jsonify({"error": "Cliente não pode ser deletado, pois está associado a uma reserva"}), 409

    # Se o cliente não estiver associado a nenhuma reserva, podemos prosseguir com a exclusão
    db.session.delete(cliente)
    db.session.commit()

    return jsonify({"message": "Cliente removido com sucesso"}), 200


@app.post('/reservas', tags=[reserva_tag], responses={"200": ReservaCreateSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_reserva(form: ReservaCreateSchema):
    """Adiciona uma nova Reserva à base de dados

    Retorna uma representação da Reserva.
    """ 
    print(form)
    quarto_id = int(form.quarto_id)
    cliente_id = int(form.cliente_id)
    print(form)
    cliente = db.session.query(Cliente).filter(Cliente.id == cliente_id).first()
    quarto = db.session.query(Quarto).filter(Quarto.id == quarto_id).first()

    if not cliente:
        return jsonify({'message' : 'Cliente não encontrado.'}), 400
    if not quarto:
        return jsonify({'message' : 'Quarto não encontrado.'}), 400

    # Verificar se o quarto está vago
    if not quarto.vago:
        return jsonify({'message' : 'O quarto já está ocupado.'}), 400
    
    # Verificar se o quarto comporta a quantidade de pessoas fornecidas
    if quarto.capacidade_maxima< form.numero_pessoas:
        return jsonify({'message' : 'O quarto não comporta a quantidade de pessoas fornecidas.'}), 400
    
    # Convertendo as strings para objetos de data Python
    data_checkin = datetime.strptime(form.data_checkin, '%Y-%m-%d').date()
    data_checkout = datetime.strptime(form.data_checkout, '%Y-%m-%d').date()

    # Criar a reserva
    reserva = Reserva(     
        quarto_id=quarto_id,
        quarto=quarto,
        data_checkin=data_checkin,
        data_checkout=data_checkout,
        numero_pessoas=form.numero_pessoas,
        cliente_id=cliente_id,
        cliente=cliente
    )

    # Atualizar o status do quarto para ocupado
    quarto.vago = False

    db.session.add(reserva)
    db.session.commit()

    return jsonify({'message': 'Reserva criada com sucesso!'}), 201

# Rota para buscar todas as reservas existentes
@app.get('/reservas', tags=[reserva_tag], responses={"200": ReservaViewSchema})
def get_reservas():
    """Lista todas as Reservas da base de dados

    Retorna uma representação da Reserva.
    """
    todas_reservas = Reserva.query.all()
    return jsonify([reserva.serialize() for reserva in todas_reservas])



@app.put('/reservas', tags=[reserva_tag], responses={"200": ReservaEditSchema, "409": ErrorSchema, "400": ErrorSchema})
def editar_reserva(query: ReservaBuscaPorIDSchema, form: ReservaEditSchema):
    """Edita uma Reserva existente na base de dados

    Retorna uma confirmação alteração.
    """
    reserva_id = int(query.id)
    reserva = Reserva.query.get(reserva_id)

    if not reserva:
        return jsonify({"message": "Reserva não encontrada"}), 404

    # Verificar se o novo número do quarto existe e está vago
    if form.quarto_id != reserva.quarto_id:
        novo_quarto = Quarto.query.get(form.quarto_id)
        if not novo_quarto:
            return jsonify({"message": "Novo número do quarto não encontrado"}), 404
        if not novo_quarto.vago:
            return jsonify({"message": "Novo quarto não está vago"}), 409

    # Verificar se o novo cliente existe
    if form.cliente_id != reserva.cliente_id:
        novo_cliente = Cliente.query.get(form.cliente_id)
        if not novo_cliente:
            return jsonify({"message": "Novo cliente não encontrado"}), 404

    # Verificar se as informações são iguais
    if (form.quarto_id == reserva.quarto_id and
        form.data_checkin == reserva.data_checkin and
        form.data_checkout == reserva.data_checkout and
        form.numero_pessoas == reserva.numero_pessoas and
        form.cliente_id == reserva.cliente_id):
        return jsonify({"message": "As informações enviadas são iguais às informações originais, não houve alteração"}), 200

    # Marcar o quarto antigo como vago
    if form.quarto_id != reserva.quarto_id:
        quarto_antigo = Quarto.query.get(reserva.quarto_id)
        quarto_antigo.vago = True
        db.session.commit()

    # Atualizar os dados da reserva
    reserva.quarto_id = form.quarto_id
    reserva.data_checkin = form.data_checkin
    reserva.data_checkout = form.data_checkout
    reserva.numero_pessoas = form.numero_pessoas
    reserva.cliente_id = form.cliente_id

    db.session.commit()

    return jsonify({"message": "Informações da reserva atualizadas com sucesso"}), 200

# Rota para excluir uma reserva existente
@app.delete('/reservas', tags=[reserva_tag], responses={"200": ReservaDelSchema, "404": ErrorSchema})
def excluir_reserva(query:ReservaBuscaPorIDSchema):
    """Deleta uma Reserva a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    reserva_id = int(query.id)
    print(f"Deletando dados referente a reserva #{reserva_id}")

    # Buscar a reserva
    reserva = db.session.query(Reserva).filter(Reserva.id == reserva_id).first()

    if not reserva:
        return jsonify({"error": f"Reserva não encontrada"}), 404

    # Obter o ID do quarto associado à reserva
    quarto_id = reserva.quarto_id

    # Buscar o quarto na tabela de quartos pelo ID
    quarto = db.session.query(Quarto).filter(Quarto.id == quarto_id).first()

    if not quarto:
        return jsonify({"error": f"Quarto associado à reserva não encontrado"}), 404

    # Marcar o quarto como vago
    quarto.vago = True

    # Remover a reserva
    db.session.delete(reserva)
    db.session.commit()
    
    return jsonify({"message": f"Reserva removida com sucesso"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
