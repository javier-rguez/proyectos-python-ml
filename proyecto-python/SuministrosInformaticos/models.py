from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import db
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

class Articulo(db.Base):
    '''Clase Articulo
    Incluye las características generales del artículo

    args
    - id_articulo = PK de la clase artículo
    - referencia = string que define la referencia de un artículo
    - nombre: string que describe el nombre del artículo
    - marca: string que describe la marca del artículo
    - precio_venta: float que compone el precio del artículo
    - stock: entero que compone el stock del articulo
    - categoria: string que describe la categoria del artículo
    - descripcion: string que describe la descripción del artículo
    - ubicacion: string que describe la ubicación en almacén del artículo
    - id_proveedor: integer que indentifica el nº de id del proveedor del artículo
    - precio_proveedor: entero que compone precio de proveedor del articulo'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = "articulo"
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {"sqlite_autoincrement": True}
    # ---definimos las columnas de nuestra tabla---
    id_articulo = Column(Integer, primary_key=True) # establecemos el id_articulo como Primary Key
    referencia = Column(String(64), unique=True) # campo único y que no se puede repetir
    nombre = Column(String(128))
    marca = Column(String(64))
    precio_venta = Column(Float)
    stock = Column(Integer)
    categoria = Column(String(64))
    descripcion = Column(String(128), default='')
    ubicacion = Column(String(64), default='')
    id_proveedor = Column(Integer, ForeignKey('proveedor.id_proveedor')) # id_proveedor como Foreign Key
    precio_proveedor = Column(Float)

    # Relación 1 a 1 con PC_Tablet
    pctablets = relationship('PC_Tablet', back_populates='articulo', cascade='all, delete-orphan',
                             passive_deletes=True, uselist=False)
    # Relación 1 a 1 con Monitor
    monitores = relationship('Monitor', back_populates='articulo', cascade='all, delete-orphan',
                             passive_deletes=True, uselist=False)
    # Relación 1 a 1 con Monitor
    almacenamientos = relationship('Almacenamiento', back_populates='articulo', cascade='all, delete-orphan',
                             passive_deletes=True, uselist=False)
    # Relación 1 a 1 con Monitor
    redes = relationship('Redes', back_populates='articulo', cascade='all, delete-orphan',
                             passive_deletes=True, uselist=False)



    # constructor de la la clase Articulo
    def __init__(self, referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion, id_proveedor,
                 precio_proveedor):
        self.referencia = referencia
        self.nombre = nombre
        self.marca = marca
        self.precio_venta = precio_venta
        self.stock = stock
        self.categoria = categoria
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.id_proveedor = id_proveedor
        self.precio_proveedor = precio_proveedor

    # método str de la clase Articulo
    def __str__(self):
        return 'Artículo: {} --> precio: {}'.format(self.nombre, self.referencia, self.precio_venta)

class PC_Tablet(Articulo):
    '''Clase PC_Tablet que hereda de Articulo
    Incluye las características particulares de los ordenadores y tablets

    args
    - resolucion = string que identifica la resolución de la pantalla
    - procesador: string que describe el procesador del ordenador o tablet
    - memoria: string que describe la memoria del ordenador o tablet
    - almacenamiento: string que describe la capacidad de almacenamiento del ordenador o tablet'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'pc-tablet'
    # ---definimos las columnas de nuestra tabla---
    id_pc_tablet = Column(Integer, primary_key=True) #establecemos el id como Primary Key
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo', ondelete='CASCADE'))
    resolucion = Column(String(64))
    procesador = Column(String(64))
    memoria = Column(String(64))
    almacenamiento = Column(String(64))

    # Relación inversa
    articulo = relationship('Articulo', back_populates='pctablets')

    # constructor de la la clase Ordenador_Tablet
    def __init__(self, referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion, id_proveedor,
                 precio_proveedor, resolucion, procesador, memoria, almacenamiento):
        super().__init__(referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                         id_proveedor, precio_proveedor)
        self.resolucion = resolucion
        self.procesador = procesador
        self.memoria = memoria
        self.almacenamiento = almacenamiento

    # método str de la clase Sobremesa
    def __str__(self):
        return (super().__str__() + '\n - resolución: {}\n - procesador: {}\n - memoria: {}\n - almacenamiento: {}'
                .format(self.resolucion, self.procesador, self.memoria, self.almacenamiento))

class Monitor(Articulo):
    '''Clase Monitor que hereda de Articulo
    Incluye las características particulares de los monitores

    args
    - tamanio = entero que define el tamaño en pulgadas del monitor
    - resolucion = string que identifica la resolución del monitor
    - altura_ajustable: string que define si la altura del monitor es ajustable
    - conexiones: string que describe las conexiones disponibles en la pantalla'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'monitor'
    # ---definimos las columnas de nuestra tabla---
    id_monitor = Column(Integer, primary_key=True) #establecemos el id como Primary Key
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo', ondelete='CASCADE'))
    tamanio = Column(String(64))
    resolucion = Column(String(64))
    altura_ajustable = Column(String(8))
    conexiones = Column(String(64))

    # Relación inversa
    articulo = relationship('Articulo', back_populates='monitores')

    # constructor de la la clase Monitor
    def __init__(self, referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion, id_proveedor,
                 precio_proveedor, tamanio, resolucion, altura_ajustable, conexiones):
        super().__init__(referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                         id_proveedor, precio_proveedor)
        self.tamanio = tamanio
        self.resolucion = resolucion
        self.altura_ajustable = altura_ajustable
        self.conexiones = conexiones

    # método str de la clase Monitor
    def __str__(self):
        return (super().__str__() + '\n - resolución: {}\n - tamaño {}\n - conexiones: {}\n'
                .format(self.resolucion, self.tamanio, self.conexiones))

class Almacenamiento(Articulo):
    '''Clase Almacenamiento que hereda de Articulo
    Incluye las características particulares de dispositivos de almacenamiento

    args
    - tipo: string que define el tipo de dispositivo de almacenamiento (interno, externo, usb)
    - capacidad: string que identifica la capacidad del almacenamiento del dispositivo
    - conexiones: string que describe las conexiones del dispositivo de almacenmiento'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'almacenamiento'
    # ---definimos las columnas de nuestra tabla---
    id_almacenamiento = Column(Integer, primary_key=True) #establecemos el id como Primary Key
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo', ondelete='CASCADE'))
    tipo = Column(String(64))
    capacidad = Column(String(64))
    conexiones = Column(String(64))

    # Relación inversa
    articulo = relationship('Articulo', back_populates='almacenamientos')

    # constructor de la la clase Almacenamiento
    def __init__(self, referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                 id_proveedor, precio_proveedor, tipo, capacidad, conexiones):
        super().__init__(referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                         id_proveedor, precio_proveedor)
        self.tipo = tipo
        self.capacidad = capacidad
        self.conexiones = conexiones

    # método str de la clase Almacenamiento
    def __str__(self):
        return (super().__str__() + '\n - tipo: {}\n - capacidad: {}\n - conexiones: {}\n'
                .format(self.tipo, self.capacidad, self.conexiones))

class Redes(Articulo):
    '''Clase Redes que hereda de Articulo
    Incluye las características particulares de dispositivos de redes o conetividad

    args
    - tipo: string que define el tipo de dispositivo (repetidor WIFI, Router, Switch...)
    - conexiones: string que describe las conexiones del dispositivo de red o conectividad'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'redes'
    # ---definimos las columnas de nuestra tabla---
    id_redes = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo', ondelete='CASCADE'))
    tipo = Column(String(64))
    conexiones = Column(String(64))

    # Relación inversa
    articulo = relationship('Articulo', back_populates='redes')

    # constructor de la la clase Redes
    def __init__(self, referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                 id_proveedor, precio_proveedor, tipo, conexiones):
        super().__init__(referencia, nombre, marca, precio_venta, stock, categoria, descripcion, ubicacion,
                         id_proveedor, precio_proveedor)
        self.tipo = tipo
        self.conexiones = conexiones

    # método str de la clase Almacenamiento
    def __str__(self):
        return (super().__str__() + '\n - tipo: {}\n - conexiones: {}\n'.format(self.tipo, self.conexiones))


class Proveedor(db.Base):
    '''Clase Proveedor
    Incluye los datos del proveedor

    args
    - id_proveedor (PK): entero que identifica el código del proveedor
    - nombre: string que describe el nombre del proveedor
    - nif: string que nos indica el NIF del proveedor
    - direccion: string que compone la dirección fiscal del proveedor
    - contacto: string que define la persona de contacto del proveedor
    - tlf_fijo: string que define el nº de teléfono fijo del proveedor
    - tlf_movil: string que define el nº de teléfono móvil del proveedor
    - correo: string que describe el email del proveedor'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'proveedor'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_proveedor = Column(Integer, primary_key=True) #establecemos el id como Primary Key
    nombre = Column(String(128))
    nif = Column(String(16), unique=True) # Sólo puede haber un proveedor con el mismo NIF
    direccion = Column(String(128))
    contacto = Column(String(64))
    tlf_fijo = Column(String(32))
    tlf_movil = Column(String(32))
    correo = Column(String(64))

    # relación 1 a N entre las entidades Proveedor y Articulo
    rel_proveedor_articulo = relationship('Articulo', backref='rel_articulo_proveedor')

    # relación 1 a N entre las entidades Pedido y Proveedor
    rel_pedido = relationship('Pedido', backref='rel_proveedor')

    # constructor de la la clase Proveedor
    def __init__(self, nombre, nif, direccion, contacto, tlf_fijo, tlf_movil, correo):
        self.nombre = nombre
        self.nif = nif
        self.direccion = direccion
        self.contacto = contacto
        self.tlf_fijo = tlf_fijo
        self.tlf_movil = tlf_movil
        self.correo = correo

    # método str de la clase Articulo
    def __str__(self):
        return ('Proveedor: {}\n - NIF: {}\n - Contacto: {}\n - Teléfono: {} / {}\n - Correo: {}'
                .format(self.nombre, self.nif, self.contacto, self.tlf_fijo, self.tlf_movil, self.correo))


class Cliente(db.Base):
    '''Clase Cliente
    Incluye los datos del cliente

    args
    - id_cliente (PK): entero que identifica el código del cliente
    - nombre: string que describe el nombre del cliente
    - nif: string que nos indica el NIF del cliente
    - direccion: string que compone la dirección fiscal del cliente
    - contacto: string que define la persona de contacto del cliente
    - tlf_fijo: string que define el nº de teléfono fijo del cliente
    - tlf_movil: string que define el nº de teléfono móvil del cliente
    - correo: string que describe el email del cliente
    - forma_pago: string que describe la forma de pago del cliente'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'cliente'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_cliente = Column(Integer, primary_key=True) #establecemos el id como Primary Key
    nombre = Column(String(128))
    nif = Column(String(16), unique=True) # sólo puede haber un cliente con el mismo NIF
    direccion = Column(String(128))
    contacto = Column(String(64))
    tlf_fijo = Column(String(32))
    tlf_movil = Column(String(32))
    correo = Column(String(64))
    forma_pago = Column(String(64))

    # relación 1 a N entre las entidades Cliente y Venta
    rel_venta = relationship('Venta', backref='rel_cliente')

    # constructor de la la clase Cliente
    def __init__(self, nombre, nif, direccion, contacto, tlf_fijo, tlf_movil, correo, forma_pago):
        self.nombre = nombre
        self.nif = nif
        self.direccion = direccion
        self.contacto = contacto
        self.tlf_fijo = tlf_fijo
        self.tlf_movil = tlf_movil
        self.correo = correo
        self.forma_pago = forma_pago

    # método str de la clase Articulo
    def __str__(self):
        return ('Cliente: {}\n - NIF: {}\n - Contacto: {}\n - Teléfono: {} / {}\n - Correo: {}\n - Pago: {}'
                .format(self.nombre, self.nif, self.contacto, self.tlf_fijo, self.tlf_movil,
                        self.correo, self.forma_pago))


class Venta(db.Base):
    '''Clase Venta
    Incluye las características generales de una Venta realizada a cliente

    args
    - id_venta (PK) = entero que identifica el nº de venta
    - id_cliente (FK): entero que relaciona la venta con el id del cliente que lo ha realizado
    - fecha: string que almacena la fecha de realización de la venta
    - total_neto: float que almacena el total neto de la venta
    - impuesto: float que almacena el impuesto a aplicar a la venta
    - total: float que almacena el total de la venta'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'venta'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_venta = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'))
    fecha = Column(Date)
    total_neto = Column(Float)
    impuesto = Column(Float)
    total = Column(Float)

    # relación 1 a N entre las entidades Venta y Detalle_venta con eliminación en cascada a Detalle_venta
    rel_detalle = relationship('Detalle_venta', backref='rel_venta', cascade='all, delete-orphan',
                             passive_deletes=True)

    # constructor de la la clase Venta

    def __init__(self, id_cliente, fecha, total_neto, impuesto, total):
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.total_neto = total_neto
        self.impuesto = impuesto
        self.total = total

    # método str de la clase Venta
    def __str__(self):
        return (' - id_cliente: {}\n - fecha: {}\n - total neto: {}\n - total bruto: {}'
                .format(self.id_cliente, self.fecha, self.total_neto, self.total))


class Detalle_venta(db.Base):
    '''Clase Detalle_venta
    Incluye las características particulares de la venta realizada a cliente

    args
    - id_detalle_venta (PK) = entero que identifica el detalle de la orden de venta
    - id_venta (FK): entero que relaciona los detalles de venta con la orden de venta
    - id_articulo (FK): entero que relaciona la identificación del artículo con el producto en cuestión
    - cantidad: entero que describe la cantidad del articulo de la venta'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'detalle_venta'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_detalle_venta = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    id_venta = Column(Integer, ForeignKey('venta.id_venta', ondelete='CASCADE'))
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo'))
    cantidad = Column(Integer)

    # relación 1 a N entre las Detalle_articulo y Articulo
    rel_articulo = relationship('Articulo', backref='rel_detalle')

    # constructor de la la clase Detalle_pedido

    def __init__(self, id_venta, id_articulo, cantidad):
        self.id_venta = id_venta
        self.id_articulo = id_articulo
        self.cantidad = cantidad

    # método str de la clase Detalle_pedido
    def __str__(self):
        return ('Detalle de venta nº: {}\n - id_articulo:\n - cantidad: {}'
                .format(self.id_venta, self.id_articulo, self.cantidad))


class Pedido(db.Base):
    '''Clase Pedido
    Incluye las características generales de un Pedido realizado a proveedor

    args
    - id_pedido (PK) = entero que identifica el nº de pedido
    - id_proveedor (FK): entero que relaciona el pedido con el id del proveedor al que se le ha realizado el pedido
    - fecha: string que almacena la fecha de realización del pedido
    - total_neto: float que almacena el total neto del pedido
    - impuesto: float que almacena el impuesto a aplicar al pedido
    - total: float que almacena el total del pedido'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'pedido'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_pedido = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    id_proveedor = Column(Integer, ForeignKey('proveedor.id_proveedor'))
    fecha = Column(Date)
    total_neto = Column(Float)
    impuesto = Column(Float)
    total = Column(Float)

    # relación 1 a n entre las entidades Pedido y Detalle_pedido con eliminación en cascada a 'Detalle_pedido'
    rel_pedido_detalle = relationship('Detalle_pedido', backref='rel_detalle_pedido', cascade='all, delete-orphan',
                             passive_deletes=True)

    # constructor de la la clase Pedido

    def __init__(self, id_proveedor, fecha, total_neto=0, impuesto=0.21, total=0):
        self.id_proveedor = id_proveedor
        self.fecha = fecha
        self.total_neto = total_neto
        self.impuesto = impuesto
        self.total = total

    # método str de la clase Detalle_pedido
    def __str__(self):
        return (' - id_proveedor: {}\n - fecha: {}\n - total neto: {}\n - total bruto: {}'
                .format(self.id_proveedor, self.fecha, self.total_neto, self.total))


class Detalle_pedido(db.Base):
    '''Clase Detalle_pedido
    Incluye las características particulares del un pedido realizado a Proveedor

    args
    - id_detalle_pedido (PK) = entero que identifica el detalle de la orden de pedido
    - id_pedido (FK): entero que relaciona los detalles del pedido con un pedido
    - id_articulo (FK): entero que relaciona la identificación del artículo con el producto en cuestión
    - cantidad: entero que describe la cantidad del articulo del pedido'''

    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'detalle_pedido'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id_detalle_pedido = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    id_pedido = Column(Integer, ForeignKey('pedido.id_pedido', ondelete='CASCADE'))
    id_articulo = Column(Integer, ForeignKey('articulo.id_articulo'))
    cantidad = Column(Integer)

    # relación 1 a n entre las Detalle_pedido y Articulo
    rel_pedido_articulo = relationship('Articulo', backref='rel_articulo_pedido')

    # constructor de la la clase Detalle_pedido

    def __init__(self, id_pedido, id_articulo, cantidad):
        self.id_pedido = id_pedido
        self.id_articulo = id_articulo
        self.cantidad = cantidad

    # método str de la clase Detalle_pedido
    def __str__(self):
        return ('Detalle de pedido nº: {}\n - id_articulo:\n - cantidad: {}'
                .format(self.id_pedido,self.id_articulo, self.cantidad))

class User(db.Base, UserMixin):
    # definimos el nombre de la tabla correspondiente en nuestra base de datos
    __tablename__ = 'usuario'
    # nos aseguramos del control de índice autoincremental y que no se repita
    __table_args__ = {'sqlite_autoincrement': True}
    # ---definimos las columnas de nuestra tabla---
    id = Column(Integer, primary_key=True)  # establecemos el id como Primary Key
    username = Column(String(10), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    type_user = Column(Boolean, default=False) #False = cliente / True = administrador

    def __init__(self, username, password, type_user):
        self.username = username
        self.password = password
        self.type_user = type_user

    def set_password(self, password):
        # método que nos permite actualizar la contraseña de usuario
        self.password = generate_password_hash(password) # hasheamos la contraseña proporcionada

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.admin

    def check_password(self, password):
        return self.password == password

    def get_cliente(self): # función que nos devuelve el cliente que está actualmente logueado
        return db.session.query(Cliente).filter_by(nif=self.username).first()
