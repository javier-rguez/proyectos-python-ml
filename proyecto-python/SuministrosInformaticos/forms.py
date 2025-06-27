from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, FloatField, IntegerField, EmailField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import HiddenField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Email, EqualTo
import db
from models import Articulo, Cliente, Proveedor, User
from werkzeug.security import check_password_hash

class Form_articulo(FlaskForm):
    '''Clase Form_new_article
        Define un formulario Flask WTF con las características en común de un artículo

        args
        - referencia = campo string que define la referencia del artículo
        - nombre: campo string que describe el nombre del artículo
        - marca: campo string que describe la marca del artículo
        - precio_venta: campo float que compone el precio del artículo
        - stock: campo integer que compone el stock del articulo
        - categoria: campo string que describe la categoria del artículo
        - descripcion: campo string que describe la descripción del artículo
        - ubicacion: campo string que describe la ubicación en almacén del artículo
        - id_proveedor: campo integer que indentifica el nº de id del proveedor del artículo
        - precio_proveedor: campo float que compone precio de proveedor del articulo'''

    # definición de los distintos campos del formulario articulo
    referencia = StringField('Referencia', validators=[
                DataRequired(message='Este campo es obligatorio'), Length(max=64)])
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio'), Length(max=128)])
    marca = StringField('Marca', validators=[DataRequired(message='Este campo es obligatorio'), Length(max=64)])
    precio_venta = FloatField('Precio venta', validators=[
                DataRequired(message='Este campo es obligatorio. Introduzca un valor númerico mayor o igual a 0.'),
                NumberRange(min=0.0, message='El valor introducido tiene que ser un valor númerico mayor o igual a 0.')])
    stock = IntegerField('Stock', validators=[
                DataRequired(message='El valor introducido tiene que ser un número entero mayor o igual a 0.'),
                NumberRange(min=0, message='El valor introducido tiene que ser un número entero mayor o igual a 0.')])
    categoria = StringField('Categoria', validators=[DataRequired(message='Este campo es obligatorio')])
    descripcion = StringField('Descripción', validators=[Length(max=128)])
    ubicacion = StringField('Ubicación', validators=[Length(max=64)])
    id_proveedor = SelectField('Proveedor', choices=[], validators=[
                DataRequired(message='Este campo es obligatorio. Por favor, seleccion un proveedor.')])
    precio_proveedor = FloatField('Precio proveedor', validators=[
                DataRequired(message='Este campo es obligatorio. Introduzca un valor númerico mayor o igual a 0.'),
                NumberRange(min=0.0, message='El valor introducido tiene que ser un valor númerico mayor o igual a 0.')])

    def __init__(self, id_articulo_actual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_articulo_actual = id_articulo_actual

    # función que evalúa si la referencia introducida en el formulario de un nuevo artículo ya existe en la BBDD...
    # ...y en caso afirmativo genera un mensaje de aviso.
    def validate_referencia(self, referencia):
        # buscamos artículos con la referencia que consta en el campo referencia del formulario...
        # ...y en el caso de edición nos aseguramos de excluir el artículo que estamos editando
        articulo = (db.session.query(Articulo).filter_by(referencia=referencia.data)
                    .filter(Articulo.id_articulo != self.id_articulo_actual).first())
        if articulo is not None: # signifca que ha encontrado un articulo en la base de datos con esa referencia
            raise ValidationError('La referencia introducida ya existe en la base de datos.')

class Form_pc_tablet(Form_articulo):
    '''Clase Form_pc_tablet que hereda de Form_new_article
        Define un formulario Flask WTF con las características particulares de un artículo de la categoría de
        Ordenadores y Tablets

        args
        - resolucion = campo string que identifica la resolución de la pantalla
        - procesador: campo string que describe el procesador del ordenador o tablet
        - memoria: campo string que describe la memoria del ordenador o tablet
        - almacenamiento: campo string que describe la capacidad de almacenamiento del ordenador o tablet'''

    # definición de los distintos campos de las características particulares de un articulo de la...
    # ...categoria Ordenadores y Tablets
    resolucion = StringField('Resolución', validators=[Length(max=64)])
    procesador = StringField('Procesador', validators=[Length(max=64)])
    memoria = StringField('Memoria', validators=[Length(max=64)])
    almacenamiento = StringField('Almacenamiento', validators=[Length(max=64)])
    submit = SubmitField('Guardar artículo')

class Form_monitor(Form_articulo):
    '''Clase Form_monitor que hereda de Form_new_article
        Define un formulario Flask WTF con las características particulares de un artículo de la categoría de
        Monitores

        args
        - tamanio = campo entero que define el tamaño en pulgadas del monitor
        - resolucion = campo string que identifica la resolución del monitor
        - altura_ajustable: campo string que define si la altura del monitor es ajustable
        - conexiones: campo string que describe las conexiones disponibles en la pantalla
        '''

    # definición de los distintos campos de las características particulares de un articulo de la...
    # ...categoria Monitores
    tamanio = StringField('Tamaño', validators=[Length(max=64)])
    resolucion = StringField('Resolución', validators=[Length(max=64)])
    altura_ajustable = SelectField('Altura ajustable', choices=[('NO', 'No'), ('SI', 'Si')])
    conexiones = StringField('Conexiones', validators=[Length(max=64)])
    submit = SubmitField('Guardar artículo')

class Form_almacenamiento(Form_articulo):
    '''Clase Form_almacenamiento que hereda de Form_new_article
        Define un formulario Flask WTF con las características particulares de un artículo de la categoría de
        Almacenamiento

        args
        - tipo: campo string que define el tipo de dispositivo de almacenamiento (interno, externo, usb)
        - capacidad: campo string que identifica la capacidad del almacenamiento del dispositivo
        - conexiones: campo string que describe las conexiones del dispositivo de almacenmiento
        '''

    # definición de los distintos campos de las características particulares de un articulo de la...
    # ...categoria Almacenamiento
    tipo = StringField('Tipo', validators=[Length(max=64)])
    capacidad = StringField('Capacidad', validators=[Length(max=64)])
    conexiones = StringField('Conexiones', validators=[Length(max=64)])
    submit = SubmitField('Guardar artículo')

class Form_redes(Form_articulo):
    '''Clase Form_redes que hereda de Form_new_article
        Define un formulario Flask WTF con las características particulares de un artículo de la categoría de
        Redes.

        args
        - tipo: campo string que define el tipo de dispositivo (repetidor WIFI, Router, Switch...)
        - conexiones: campo string que describe las conexiones del dispositivo de red o conectividad'''

    # definición de los distintos campos de las características particulares de un articulo de la...
    # ...categoria Redes
    tipo = StringField('Tipo', validators=[Length(max=64)])
    conexiones = StringField('Conexiones', validators=[Length(max=64)])
    submit = SubmitField('Guardar artículo')


class Form_cliente(FlaskForm):
    '''Clase Form_cliente
        Define un formulario Flask WTF con los campos que definen a un cliente

        args
        - nombre: campo string que describe el nombre del cliente
        - nif: campo string que describe el NIF del cliente
        - direccion: campo string que describe la dirección del cliente
        - contacto: campo string que describe la persona de contacto del cliente
        - tlf_fijo: campo string que describe el número de teléfono fijo del cliente
        - tlf_movil: campo string que describe el número de teléfono móvil del cliente
        - correo: campo email que describe el correo electrónico del cliente
        - forma_pago: campo string que describe la forma de pago del cliente'''

    # definición de los distintos campos del formulario cliente
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio'),
                                               Length(max=128)])
    nif = StringField('NIF', validators=[DataRequired(message='Este campo es obligatorio'), Length(max=9)])
    direccion = StringField('Dirección', validators=[Length(max=128)])
    contacto = StringField('Contacto', validators=[Length(max=64)])
    tlf_fijo = StringField('Tlf. Fijo', validators=[Length(max=32)])
    tlf_movil = StringField('Tlf. Móvil', validators=[Length(max=32)])
    correo = EmailField('Correo electrónico', validators=[DataRequired(message='Este campo es obligatorio'),
                                            Email(message='Por favor, ingrese un email válido.'), Length(max=64)])
    forma_pago = StringField('Forma de pago', validators=[Length(max=64)])
    submit = SubmitField('Guardar cliente')

    def __init__(self, id_cliente_actual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_cliente_actual = id_cliente_actual

    # función que evalúa si el NIF introducido en el formulario de un nuevo cliente ya existe en la BBDD...
    # ...y en caso afirmativo general un mensaje de aviso.
    def validate_nif(self, nif):
        # buscamos clientes con el nif que consta en el campo nif del formulario...
        # ...y en el caso de edición nos aseguramos de excluir el nif que estamos editando
        cliente = db.session.query(Cliente).filter_by(nif=nif.data).filter(Cliente.id_cliente != self.id_cliente_actual).first()
        if cliente is not None: # signifca que ha encontrado un cliente en la base de datos con ese NIF
            raise ValidationError('El NIF introducida ya existe en la base de datos.')

class Form_proveedor(FlaskForm):
    '''Clase Form_proveedor
        Define un formulario Flask WTF con los campos que definen a un proveedor

        args
        - nombre: campo string que describe el nombre del proveedor
        - nif: campo string que describe el NIF del proveedor
        - direccion: campo string que describe la dirección del proveedor
        - contacto: campo string que describe la persona de contacto del proveedor
        - tlf_fijo: campo string que describe el número de teléfono fijo del proveedor
        - tlf_movil: campo string que describe el número de teléfono móvil del proveedor
        - correo: campo email que describe el correo electrónico del proveedor'''

    # definición de los distintos campos del formulario proveedor
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio'),
                                               Length(max=128)])
    nif = StringField('NIF', validators=[DataRequired(message='Este campo es obligatorio'), Length(max=9)])
    direccion = StringField('Dirección', validators=[Length(max=128)])
    contacto = StringField('Contacto', validators=[Length(max=64)])
    tlf_fijo = StringField('Tlf. Fijo', validators=[Length(max=32)])
    tlf_movil = StringField('Tlf. Móvil', validators=[Length(max=32)])
    correo = EmailField('Correo electrónico', validators=[DataRequired(message='Este campo es obligatorio'),
                                            Email(message='Por favor, ingrese un email válido.'), Length(max=64)])
    submit = SubmitField('Guardar proveedor')

    def __init__(self, id_proveedor_actual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_proveedor_actual = id_proveedor_actual
    # validador personalizado: función que evalúa si el NIF introducida en el formulario de un nuevo proveedor...
    # ...ya existe en la BBDD y en caso afirmativo general un mensaje de aviso.
    def validate_nif(self, nif):
        # buscamos proveedores con el nif que consta en el campo nif del formulario...
        # ...y en el caso de edición nos aseguramos de excluir el nif que estamos editando
        proveedor = db.session.query(Proveedor).filter_by(nif=nif.data).filter(Proveedor.id_proveedor != self.id_proveedor_actual).first()
        if proveedor is not None: # signifca que ha encontrado un proveedor en la base de datos con ese cif
            raise ValidationError('El NIF introducida ya existe en la base de datos.')


class Form_venta(FlaskForm):
    '''Clase Form_venta
        Define un formulario Flask WTF con los datos relacionados con la venta

        args
        - nombre_cliente: campo string que el usuario usará para buscar al cliente por su nombre
        - id_cliente: campo oculto que almacenará el id del cliente seleccionado para la nueva venta
        - fecha: campo string que describe la fecha de la venta
        - total_neto: campo float que describe el precio total neto de la venta
        - impuesto: campo float que describe el valor del tipo de impuesto aplicable a la venta
        - total: campo float que describe el precio total de la venta'''

    # definición de los distintos campos del formulario articulo
    nombre_cliente = StringField('Cliente', validators=[DataRequired()])
    id_cliente = HiddenField('id_cliente', validators=[DataRequired()]) # campo oculto para almacenar el ID del cliente seleccionado
    fecha = DateField('Fecha', format='%d-%m-%Y')
    total_neto = FloatField('Total')
    impuesto = SelectField('Impuesto', choices=[(0.21, 'IVA (21%)'), (0.07, 'IGIC (7%)')], validators=[
        DataRequired(message='Este campo es obligatorio. Por favor, seleccion un tipo de impuesto.')])
    total = FloatField('Total')
    submit = SubmitField('Crear venta')

    # Validador personalizado: función para verificar que el cliente introducido existe
    def validate_nombre_cliente(self, field):
        # Comprobamos si 'id_cliente' del campo oculto de la plantilla crear-venta.html corresponde a un cliente de la BBDD
        cliente = db.session.query(Cliente).get(self.id_cliente.data)
        if not cliente: # si no existe lanzamos error
            raise ValidationError('El cliente seleccionado no es válido. Por favor, elija uno de la lista.')

class Form_add_articulo(FlaskForm):
    '''Clase Form_add_articulo
            Define un formulario Flask WTF con los datos necesarios para añadir un artículo a una venta o un pedido

            args
            - referencia_nombre: campo string que el usuario usará para buscar artículo por su nombre o referencia
            - id_articulo: campo oculto que almacenará el id del artículo seleccionado para la nueva venta o pedido
            - cantidad: campo entero que indica la cantidad del artículo selecciona para añadir a la venta o pedido
            - es_pedido: campo booleano que indentifica si se trata de una venta o un pedido'''
    referencia_nombre = StringField('Artículo o Referencia',
                                    validators=[DataRequired(message='Este campo es obligatorio')])
    id_articulo = HiddenField('id_articulo', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(message='Este campo es obligatorio'),
                                                    NumberRange(min=1, message='La cantidad debe ser al menos 1.')])
    submit = SubmitField('Añadir artículo')
    es_pedido = False  # atributo para identificar si el formulario se usa para una Venta o un Pedido

    # Validador personalizado: comprobamos si el artículo itroducido existe
    def validate_referencia_nombre(self, field):
        articulo = db.session.query(Articulo).get(self.id_articulo.data)
        if not articulo:
            raise ValidationError('El artículo seleccionado no es válido.')

    # Validador personalizado: comprobamos si hay stock suficiente del artículo en caso de añadir a una venta
    def validate_cantidad(self, field):
        if self.es_pedido == True: # si se trata de un pedido no es necesario hacer la validación de stock
            return
        else:
            articulo = db.session.query(Articulo).get(self.id_articulo.data)
            if articulo:
                if articulo.stock < self.cantidad.data:
                    raise ValidationError(f'Stock insuficiente para el artículo seleccionado. Stock disponible: {articulo.stock} uds')

class Form_pedido(FlaskForm):
    '''Clase Form_pedido
        Define un formulario Flask WTF con los datos relacionados con el pedido

        args
        - nombre_proveedor: campo string que el usuario usará para buscar al proveedor por su nombre
        - id_proveedor: campo oculto que almacenará el id del proveedor seleccionado para el nuevo pedido
        - fecha: campo string que describe la fecha del pedido
        - total_neto: campo float que describe el precio total neto del pedido
        - impuesto: campo float que describe el valor del tipo de impuesto aplicable al pedido
        - total: campo float que describe el precio total del pedido'''

    # definición de los distintos campos del formulario pedido
    nombre_proveedor = StringField('Proveedor', validators=[DataRequired()])
    # campo oculto para almacenar el ID del proveedor seleccionado
    id_proveedor = HiddenField('id_proveedor', validators=[DataRequired()])
    fecha = DateField('Fecha', format='%d-%m-%Y')
    total_neto = FloatField('Total')
    impuesto = SelectField('Impuesto', choices=[(0.21, 'IVA (21%)'), (0.07, 'IGIC (7%)')], validators=[
        DataRequired(message='Este campo es obligatorio. Por favor, seleccion un tipo de impuesto.')])
    total = FloatField('Total')
    submit = SubmitField('Crear pedido')

    # Validador personalizado: función para verificar que el proveedor introducido existe
    def validate_nombre_proveedor(self, field):
        # Comprobamos si 'id_proveedor' del campo oculto de la plantilla crear-pedido.html corresponde a un proveedor de la BBDD
        proveedor = db.session.query(Proveedor).get(self.id_proveedor.data)
        if not proveedor: # si no existe lanzamos error
            raise ValidationError('El proveedor seleccionado no es válido. Por favor, elija uno de la lista.')

class Form_analisis(FlaskForm):
    '''Clase Form_analisis
        Define un formulario Flask WTF con los campos que definen el criterio de búsqueda del análisis

        args
        - fecha_inicio: campo string que describe el nombre del cliente
        - fecha_fin: campo string que describe el NIF del cliente
        - modelo: campo string que describe el modelo en el que se desea realizar la consulta: Ventas o Pedidos
        - periodicidad: campo string que describe el la periodicidad del la consulta: mensual o anual'''

    # definición de los distintos campos del formulario de analisis
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired(message='Este campo es obligatorio')])
    fecha_fin = DateField('Fecha de fin', validators=[DataRequired(message='Este campo es obligatorio')])
    modelo = SelectField('Seleccionar categoría de búsqueda',
                                choices=[('Pedido', 'Pedidos'),('Venta', 'Ventas'),('Beneficio', 'Beneficios')],
                                validators=[DataRequired()])
    periodicidad = SelectField('Seleccionar periodicidad de la consulta',
                               choices=[('mensual','Mensual'), ('anual', 'Anual')], validators=[DataRequired()])
    submit = SubmitField('Realizar consulta')

    # Validador a nivel de formulario: sobreescribimos método validate para poder hacer la validación personalizada...
    # ...entre dos campos: fecha_inicio y fecha_fin.
    def validate(self, extra_validators=None):
        # ejecutamos primero las validaciones configuradas en la declaración de los parámetros del formulario antes...
        # ...que las personalizadas
        if not super().validate(extra_validators):
            return False

        # validación personalizada de rango de fechas correcto
        if self.fecha_inicio.data > self.fecha_fin.data:
            self.fecha_inicio.errors.append(
                'Periodo seleccionado erróneo: la fecha de inicio no puede ser posterior a la fecha de fin.')
            return False

        return True # en caso de superar las validaciones retornamos un True

class Form_analisis_cliente(FlaskForm):
    '''Clase Form_analisis_cliente
        Define un formulario Flask WTF con los campos que definen el criterio de búsqueda del análisis

        args
        - fecha_inicio: campo string que describe el nombre del cliente
        - fecha_fin: campo string que describe el NIF del cliente
        - periodicidad: campo string que describe el la periodicidad del la consulta: mensual o anual'''

    # definición de los distintos campos del formulario de analisis
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired(message='Este campo es obligatorio')])
    fecha_fin = DateField('Fecha de fin', validators=[DataRequired(message='Este campo es obligatorio')])
    periodicidad = SelectField('Seleccionar periodicidad de la consulta',
                               choices=[('mensual','Mensual'), ('anual', 'Anual')], validators=[DataRequired()])
    submit = SubmitField('Realizar consulta')

    # Validador a nivel de formulario: sobreescribimos método validate para poder hacer la validación personalizada...
    # ...entre dos campos: fecha_inicio y fecha_fin.
    def validate(self, extra_validators=None):
        # ejecutamos primero las validaciones configuradas en la declaración de los parámetros del formulario antes...
        # ...que las personalizadas
        if not super().validate(extra_validators):
            return False

        # validación personalizada de rango de fechas correcto
        if self.fecha_inicio.data > self.fecha_fin.data:
            self.fecha_inicio.errors.append(
                'Periodo seleccionado erróneo: la fecha de inicio no puede ser posterior a la fecha de fin.')
            return False

        return True # en caso de superar las validaciones retornamos un True

class Form_login(FlaskForm):
    '''Clase Form_login
            Define un formulario Flask WTF con los campos de acceso para un usuario loguearse

            args
            - username: campo string que describe el nombre del cliente
            - password: campo de tipo contraseña que define la contraseña del usuario
            - type_user: campo de selección de tipo de usuario que tiene las opciones de Cliente o Administrador'''
    username = StringField('Usuario', validators=[DataRequired(message='Este campo es obligatorio')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='Este campo es obligatorio')])
    type_user = SelectField('Tipo de usuario', choices=[('0', 'Cliente'), ('1', 'Administrador')])
    submit = SubmitField('Acceder')

    def validate_username(self, username):
        # comprobamos si el usuario existe en la base de datos
        self.user = db.session.query(User).filter_by(username=username.data).first()
        if self.user is None:
            raise ValidationError('El usuario no existe en la base de datos.')

    def validate_password(self, password):
        # validamos si la contraseña existe sólo en caso de que el usuario existe
        if not hasattr(self, 'user') or self.user is None:
            return
        if not check_password_hash(self.user.password, password.data):
            raise ValidationError('La contraseña introducida es incorrecta.')
        # validamos si el tipo de usuario es correcto
        if self.user.type_user is not bool(int(self.type_user.data)):
            raise ValidationError('El tipo de usuario seleccionado es incorrecto.')

class Form_update_pass(FlaskForm):
    current_pass = PasswordField('Contraseña actual',
                                 validators=[DataRequired(message='La contraseña actual es obligatoria.')])
    new_pass = PasswordField('Nueva contraseña', validators=[
        DataRequired(message='La nueva contraseña es obligatoria.'),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres.')])
    confirm_pass = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Debe confirmar la nueva contraseña.'),
        EqualTo('new_pass', message='Las contraseñas no coinciden.')])
    submit = SubmitField('Actualizar contraseña')

    def validate_current_pass(self, current_pass):
        # Comprobamos si la contraseña actual coincide con la del usuario autenticado
        user = db.session.query(User).get(current_user.id)
        if not user or not check_password_hash(user.password, current_pass.data):
            raise ValidationError('La contraseña actual es incorrecta.')

    def validate_new_pass(self, new_pass):
        # Nos aseguramos de que la nueva contraseña sea diferente de la actual
        if new_pass.data == self.current_pass.data:
            raise ValidationError('La nueva contraseña no puede ser igual a la contraseña actual.')

class Form_usuario(FlaskForm):
    '''Clase Form_usuario
            Define un formulario Flask WTF con los campos de acceso para un usuario loguearse

            args
            - username: campo string que define el nombre del usuario (en NIF de la empresa es el nombre de usuario)
            - password: campo string que define la contraseña de acceso del usuario
            - type_user: campo booleano que define el tipo de usuario: Cliente o Administrador'''
    username = StringField('Usuario', validators=[DataRequired(message='Este campo es obligatorio')])
    password = PasswordField('Contraseña', validators=[DataRequired(message='Este campo es obligatorio')])
    type_user = SelectField('Tipo de usuario', choices=[(0, 'Cliente'), (1, 'Administrador')])
    submit = SubmitField('Guardar usuario')

    def __init__(self, id_usuario_actual=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_usuario_actual = id_usuario_actual

    # validador personalizado: función que evalúa si el username introducido en el formulario de un nuevo usuario...
    # ...ya existe en la BBDD y en caso afirmativo general un mensaje de aviso.
    def validate_username(self, username):
        # buscamos usuarios con el username que consta en el campo username del formulario...
        # ...y en el caso de edición nos aseguramos de excluir el username que estamos editando
        usuario = db.session.query(User).filter_by(username=username.data).filter(User.id != self.id_usuario_actual).first()
        if usuario is not None: # signifca que ha encontrado un usuario en la base de datos con ese username
            raise ValidationError('El nombre de usuario introducido ya existe en la base de datos.')

class Form_eliminar_registro(FlaskForm):
    '''Clase Form_eliminar_registro
            Define un formulario Flask WTF que confirma la eliminación de un registro de la base de datos'''
    submit = SubmitField('Confirmar')

