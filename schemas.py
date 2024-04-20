import re
from pydantic import BaseModel, validator, EmailStr
from datetime import date, datetime
from pydantic.error_wrappers import ValidationError
from models import *
from pydantic import BaseModel


#SCHEMAS REFERENTE AOS QUARTOS:


class QuartoCreateSchema(BaseModel):
    numero: int = 101
    capacidade_maxima: int = 2
    valor_diaria: float = 400
    vago: bool = True

    @validator('capacidade_maxima')
    def check_capacidade_maxima(cls, value):
        if value < 1 or value > 6:
            raise ValueError("A capacidade máxima do quarto deve estar entre 1 e 6")
        return value

    @validator('valor_diaria')
    def check_valor_diaria(cls, value):
        if value <= 0:
            raise ValueError("O valor da diária deve ser maior que zero")
        if value > 2000:
            raise ValueError("O valor da diária não pode exceder 2000")
        return value
    
    @validator('vago')
    def check_vago(cls, value):
        if not isinstance(value, bool):
            raise ValueError("O campo 'vago' deve ser um booleano (True ou False)")
        return value
    
    @validator('numero')
    def check_numero(cls, value):
        if value < 1 or value > 5000:
            raise ValueError("O número do quarto deve estar entre 1 e 5000")
        if Quarto.query.filter_by(numero=value).first():
            raise ValueError("O número do quarto já está em uso")
        return value
    
def apresenta_quarto(quarto: Quarto):
    """ Retorna uma representação do quarto seguindo o schema definido em
        QuartoViewSchema.
    """
    return {
        "id": quarto.id,
        "numero": quarto.numero,
        "capacidade_maxima": quarto.capacidade_maxima,
        "valor_diaria": quarto.valor_diaria,
        "vago": quarto.vago,
    }    
    
class QuartoEditSchema(BaseModel):
    numero: int = 101
    capacidade_maxima: int = 2
    valor_diaria: float = 400
    vago: bool = False

    @validator('capacidade_maxima')
    def check_capacidade_maxima(cls, value):
        if value < 1 or value > 6:
            raise ValueError("A capacidade máxima do quarto deve estar entre 1 e 6")
        return value

    @validator('valor_diaria')
    def check_valor_diaria(cls, value):
        if value <= 0:
            raise ValueError("O valor da diária deve ser maior que zero")
        if value > 2000:
            raise ValueError("O valor da diária não pode exceder 2000")
        return value
    
    @validator('vago')
    def check_vago(cls, value):
        if not isinstance(value, bool):
            raise ValueError("O campo 'vago' deve ser um booleano (True ou False)")
        return value
    
class QuartoViewSchema(BaseModel):
    id: int = 1
    numero: int = 101
    capacidade_maxima: int = 2
    valor_diaria: float = 400
    vago: bool = 1

class QuartoBuscaPorIDSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no ID do quarto.
    """
    id: int = "1"   
    
class QuartoDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    id: int


#SCHEMAS REFERENTE AOS CLIENTES:


class ClienteCreateSchema(BaseModel):
    nome: str = 'Juan'
    sobrenome: str = 'Azevedo'
    celular: str = '21996289958'
    email: EmailStr = 'juanmatheus@gmail.com'

    @validator('nome', 'sobrenome')
    def check_nome_sobrenome(cls, value):
        if not re.match("^[A-Za-z]+$", value):
            raise ValueError("O campo 'nome' ou 'sobrenome' deve conter apenas letras")
        return value

    @validator('celular')
    def check_celular(cls, value):
        if not re.match("^[0-9]{11}$", value):
            raise ValueError("O campo 'celular' deve conter exatamente 11 dígitos")
        return value
    
def apresenta_cliente(cliente: Cliente):
    """ Retorna uma representação de um cliente seguindo o schema definido em
        ClienteViewSchema.
    """
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "sobrenome": cliente.sobrenome,
        "celular": cliente.celular,
        "email": cliente.email,
    }   
       

class ClienteEditSchema(BaseModel):
    nome: str = 'Juan'
    sobrenome: str = 'Azevedo'
    celular: str = '21996289958'
    email: EmailStr = 'juanmatheus@gmail.com'

    @validator('nome', 'sobrenome')
    def check_nome_sobrenome(cls, value):
        if not re.match("^[A-Za-z]+$", value):
            raise ValueError("O campo 'nome' ou 'sobrenome' deve conter apenas letras")
        return value

    @validator('celular')
    def check_celular(cls, value):
        if not re.match("^[0-9]{11}$", value):
            raise ValueError("O campo 'celular' deve conter exatamente 11 dígitos")
        return value

class ClienteViewSchema(BaseModel):
    id: int = 1
    nome: str = 'Juan'
    sobrenome: str = 'Azevedo'
    celular: str = '21996289958'
    email: EmailStr = 'juanmatheus@gmail.com' 

class ClienteDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    id: int

class ClienteBuscaPorIDSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no ID do quarto.
    """
    id: int = "1"   


#SCHEMAS REFERENTE AS RESERVAS:

class ReservaCreateSchema(BaseModel):
    quarto_id: int = 1
    data_checkin: str = "2025-01-01"
    data_checkout: str = "2025-01-02"
    numero_pessoas: int = 2
    cliente_id: int = 1

    @validator('data_checkin', 'data_checkout')
    def check_date_format(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError("O formato da data deve ser YYYY-MM-DD")
        return value

    @validator('data_checkin')
    def check_data_checkin(cls, value, values):
        try:
            data_checkin = datetime.strptime(value, '%Y-%m-%d').date()
            if data_checkin < date.today():
                raise ValueError("A data de check-in não pode ser no passado")
        except ValueError:
            raise ValueError("A data de check-in não é válida")
        return value

    @validator('data_checkout')
    def check_data_checkout(cls, value, values):
        try:
            data_checkout = datetime.strptime(value, '%Y-%m-%d').date()
            data_checkin = datetime.strptime(values.get('data_checkin'), '%Y-%m-%d').date()
            if data_checkout <= data_checkin:
                raise ValueError("A data de check-out deve ser posterior à data de check-in")
        except ValueError:
            raise ValueError("A data de check-out não é válida")
        return value

    @validator('numero_pessoas')
    def check_numero_pessoas(cls, value):
        if value <= 0 or value > 4:
            raise ValueError("A capacidade máxima do quarto deve estar entre 1 e 4")
        return value


def apresenta_reserva(reserva: Reserva):
    """ Retorna uma representação do Reserva seguindo o schema definido em
        ReservaViewSchema.
    """
    return {
        'id': reserva.id,
        'quarto_id': reserva.quarto_id,
        'data_checkin': reserva.data_checkin.isoformat(),
        'data_checkout': reserva.data_checkout.isoformat(),
        'numero_pessoas': reserva.numero_pessoas,
        'cliente_id': reserva.cliente_id,
        'nome': reserva.cliente,
    }    

class ReservaEditSchema(BaseModel):
    quarto_id: int = 1
    data_checkin: str = "2025-01-01"
    data_checkout: str = "2025-01-02"
    numero_pessoas: int = 2
    cliente_id: int = 1

    @validator('data_checkin')
    def check_data_checkin(cls, value):
        data_checkin = datetime.strptime(value, '%Y-%m-%d').date()
        if data_checkin < date.today():
            raise ValueError("A data de check-in não pode ser no passado")
        return data_checkin
    @validator('data_checkout')
    def check_data_checkout(cls, value, values):
        data_checkout = datetime.strptime(value, '%Y-%m-%d').date()
        data_checkin = values.get('data_checkin')
        if data_checkout <= data_checkin:
            raise ValueError("A data de check-out deve ser posterior à data de check-in")
        return data_checkout
    @validator('numero_pessoas')
    def check_numero_pessoas(cls, value):
        if value <= 0 or value > 4:
            raise ValueError("A capacidade máxima do quarto deve estar entre 1 e 4")
        return value


class ReservaViewSchema(BaseModel):
    id: int = 1
    quarto_id: int = 2
    numero_quarto: int = 102
    data_checkin: str = "2025-01-01"
    data_checkout: str = "2025-01-02"
    numero_pessoas: int = 2
    cliente_id: int = 2
    nome: str = 'Juan'
    sobrenome: str = 'Azevedo'

class ReservaBuscaPorIDSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no ID da reserva.
    """
    id: int = "1"  

class ReservaDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    id: int

class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro será representada
    """
    mesage: str