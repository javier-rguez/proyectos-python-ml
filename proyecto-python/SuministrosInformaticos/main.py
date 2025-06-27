import secrets
from datetime import date, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

from models import Proveedor, Cliente, PC_Tablet, Monitor, Pedido, Detalle_pedido, Detalle_venta, Venta, \
    Almacenamiento, Redes
from forms import Form_pc_tablet, Form_monitor, Form_almacenamiento, Form_redes, Form_articulo, Form_cliente, \
    Form_proveedor, Form_venta, Form_add_articulo, Form_eliminar_registro, Form_pedido, Form_analisis, \
    Form_analisis_cliente, Form_login, Form_update_pass, Form_usuario
from functions import get_provedores, analisis_financiero, guardar_registro, admin_required
import db
from models import User, Articulo

#####------------------------------------CONFIGURACIÓN DEL SERVIDOR FLASK------------------------------------------#####
app = Flask(__name__) # inicialización del servidor web de Flask
app.secret_key = secrets.token_hex(32) # Generamos una clave secreta aleatoria de 32 bytes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) # cierra la sesión tras 30 minutos de inactividad
login_manager = LoginManager(app) # configuración de administrador de inicio de sesión
login_manager.login_view = 'home' # en caso de no estar autenticado redirige a la vista principal home


#####----------------------------------RUTA Y FUNCIONES DE INICIO DE SESIÓN----------------------------------------#####
# función que define la página de inicio de sesión para los usuarios
@app.route('/', methods=['GET', 'POST']) # endpoint de la ruta raíz => accede a 127.0.0.1:5000
def home():
    form = Form_login() # instanciamos el formulario de login
    if form.validate_on_submit(): # si la validación de usuario, contraseña y tipo de usuario es correcta hacemos login
        username = form.username.data
        user = db.session.query(User).filter_by(username=username).first()
        login_user(user) # hacemos login
        session.permanent = True # marcamos la sesión como permanente para
        flash('Inicio de sesión realizado con éxito.', 'success')
        if user.type_user == False:  # si el tipo de usuario es cliente
            return redirect(url_for('protected'))  # accedemos a vista personalizada del cliente
        else:  # si el tipo de usuario es administrador
            return redirect(url_for('protected_admin'))  # accedemos a vista administrador
    return render_template('index.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    # Carga el usuario desde la base de datos
    return db.session.get(User, user_id)

# definimos ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'Sesión de usuario cerrada correctamente.', 'success')
    return redirect(url_for('home'))

# definimos ruta de acceso para un usuario tipo cliente
@app.route('/protected')
@login_required
def protected():
    # Vista protegida que solo se puede acceder con autenticación de cliente
    return render_template('usuario.html')

# definimos ruta de acceso para un usuario tipo administrador
@app.route('/protected_admin')
@login_required
@admin_required
def protected_admin():
    # Vista protegida que solo se puede acceder con autenticación de administrador
    return render_template('admin.html')


#####---------------------------RUTAS DE ACCESO DE USUARIO TIPO ADMINISTRADOR--------------------------------------#####
# definimos ruta para acceder al listado de artículos paginados por parte del administrador
@app.route('/protected_admin/articulos', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/articulos?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def articulo(page, per_page):
    lista_articulos = db.session.query(Articulo).all() # extraemos todos los articulos de la base de datos
    total = len(lista_articulos)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de artículos dependiendo de la página en la que estemos
    pagination_items = lista_articulos[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla artículo facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('articulos.html', lista_articulos=pagination_items,
                           pagination=pagination)

# definimos ruta que nos carga la plantilla seleccionar-categoria.html
@app.route('/protected_admin/articulos/seleccionar_categoria')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def seleccionar_categoria(): # funcion que nos carga el template 'seleccionar-categoria.html'
    # cargamos el template 'seleccionar-categoria.html'
    return render_template('seleccionar-categoria.html')

@app.route('/protected_admin/articulos/crear_articulo', methods=['POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_articulo(): # función que nos carga el template 'crear-articulo.html'
    categoria = request.form['categoria']
    form = Form_articulo()
    # dependiendo del tipo de categoría del nuevo artículo a crear, tendremos un objeto de la clase correspondiente
    if categoria == 'Ordenadores y Tablets': # si se cumple la condición creamos un objeto de la clase PC_Tablet
        form = Form_pc_tablet() # instanciamos la clase Form_pc_tablet
        # enviamos la lista de selección 'choices' para el SelectField del campo id_proveedor de nuestro formulario
        form.id_proveedor.choices = get_provedores()
        # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
        if form.validate_on_submit():
            referencia = form.referencia.data
            nombre = form.nombre.data
            marca = form.marca.data
            precio_venta = form.precio_venta.data
            stock = form.stock.data
            descripcion = form.descripcion.data
            ubicacion = form.ubicacion.data
            id_proveedor = form.id_proveedor.data
            precio_proveedor = form.precio_proveedor.data
            resolucion = form.resolucion.data
            procesador = form.procesador.data
            memoria = form.memoria.data
            almacenamiento = form.almacenamiento.data
            nuevo_articulo = PC_Tablet(referencia, nombre, marca, precio_venta, stock, categoria, descripcion,
                                       ubicacion, id_proveedor, precio_proveedor, resolucion, procesador,
                                       memoria, almacenamiento)

            # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
            if guardar_registro(nuevo_articulo):
            # si no hay error al guardar en la BBDD mensaje de éxito para imprimir con 'flash messages' en el html
                flash('Nuevo artículo creado con éxito.', 'success')
                return redirect(url_for('articulo')) # redireccionamos a la función que nos carga de nuevo articulos.html

    elif categoria == 'Monitores': # si se cumple la condición creamos un objeto de la clase  Monitores
        form = Form_monitor() # instanciamos la clase Form_monitor
        form.id_proveedor.choices = get_provedores() # enviamos lista proveedores para su selección
        # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
        if form.validate_on_submit():
            referencia = form.referencia.data
            nombre = form.nombre.data
            marca = form.marca.data
            precio_venta = form.precio_venta.data
            stock = form.stock.data
            descripcion = form.descripcion.data
            ubicacion = form.ubicacion.data
            id_proveedor = form.id_proveedor.data
            precio_proveedor = form.precio_proveedor.data
            tamanio = form.tamanio.data
            resolucion = form.resolucion.data
            altura_ajustable = form.altura_ajustable.data
            conexiones = form.conexiones.data
            nuevo_articulo = Monitor(referencia, nombre, marca, precio_venta, stock, categoria, descripcion,
                                       ubicacion, id_proveedor, precio_proveedor, tamanio, resolucion, altura_ajustable,
                                       conexiones)
            # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
            if guardar_registro(nuevo_articulo):
                # si no hay error al guardar el registro en la BBDD mensaje de exito para imprimir con 'flash messages'
                flash('Nuevo artículo creado con éxito.', 'success')
                return redirect(
                    url_for('articulo'))  # redireccionamos a la función que nos carga de nuevo articulos.html

    elif categoria == 'Almacenamiento': # si se cumple la condición creamos un objeto de la clase  Almacenamiento
        form = Form_almacenamiento() # instanciamos la clase Form_almacenamiento
        form.id_proveedor.choices = get_provedores()  # enviamos lista proveedores para su selección
        # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
        if form.validate_on_submit():
            referencia = form.referencia.data
            nombre = form.nombre.data
            marca = form.marca.data
            precio_venta = form.precio_venta.data
            stock = form.stock.data
            descripcion = form.descripcion.data
            ubicacion = form.ubicacion.data
            id_proveedor = form.id_proveedor.data
            precio_proveedor = form.precio_proveedor.data
            tipo = form.tipo.data
            capacidad = form.capacidad.data
            conexiones = form.conexiones.data
            nuevo_articulo = Almacenamiento(referencia, nombre, marca, precio_venta, stock, categoria, descripcion,
                                       ubicacion, id_proveedor, precio_proveedor, tipo, capacidad, conexiones)
            # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
            if guardar_registro(nuevo_articulo):
                # si no hay error al guardar el registro en la BBDD mensaje de exito para imprimir con 'flash messages'
                flash('Nuevo artículo creado con éxito.', 'success')
                return redirect(
                    url_for('articulo'))  # redireccionamos a la función que nos carga de nuevo articulos.html

    elif categoria == 'Redes': # si se cumple la condición creamos un objeto de la clase Redes
        form = Form_redes() # instanciamos la clase Form_redes
        form.id_proveedor.choices = get_provedores()  # enviamos lista proveedores para su selección
        # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
        if form.validate_on_submit():
            referencia = form.referencia.data
            nombre = form.nombre.data
            marca = form.marca.data
            precio_venta = form.precio_venta.data
            stock = form.stock.data
            descripcion = form.descripcion.data
            ubicacion = form.ubicacion.data
            id_proveedor = form.id_proveedor.data
            precio_proveedor = form.precio_proveedor.data
            tipo = form.tipo.data
            conexiones = form.conexiones.data
            nuevo_articulo = Redes(referencia, nombre, marca, precio_venta, stock, categoria, descripcion,
                                       ubicacion, id_proveedor, precio_proveedor, tipo, conexiones)
            # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
            if guardar_registro(nuevo_articulo):
                # si no hay error al guardar el registro en la BBDD mensaje de exito para imprimir con 'flash messages'
                flash('Nuevo artículo creado con éxito.', 'success')
                return redirect(
                    url_for('articulo'))  # redireccionamos a la función que nos carga de nuevo articulos.html

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-articulo.html', categoria=categoria, form=form)


@app.route('/protected_admin/articulos/info_adicional/<id_articulo>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'info-adicional.html' del artículo correspondiente cuando se solicita
def info_adicional(id_articulo):
    # obtenemos el artículo seleccionado a través de su id
    articulo = db.session.query(Articulo).filter_by(id_articulo=int(id_articulo)).first()
    # comprobamos el tipo de categoría y obtenemos la información de la tabla articulo...
    # ...y de la tabla con la información adicional según el tipo de artículo
    if articulo.categoria == 'Ordenadores y Tablets':
        articulo = db.session.query(PC_Tablet).filter_by(id_articulo=int(id_articulo)).first()
    elif articulo.categoria == 'Monitores':
        articulo = db.session.query(Monitor).filter_by(id_articulo=int(id_articulo)).first()
    elif articulo.categoria == 'Almacenamiento':
        articulo = db.session.query(Almacenamiento).filter_by(id_articulo=int(id_articulo)).first()
    else:
        articulo = db.session.query(Redes).filter_by(id_articulo=int(id_articulo)).first()
    # cargamos el template con la información adicional de articulo en cuestión
    return render_template('info-adicional.html', articulo=articulo)

@app.route('/protected_admin/articulos/editar_articulo/<id_articulo>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'editar-articulo.html' a partir del id_articulo del artículo a editar
def editar_articulo(id_articulo):
    # obtenemos el artículo a editar a través de su id
    articulo = db.session.query(Articulo).filter_by(id_articulo=int(id_articulo)).first()
    # comprobamos el tipo de categoría para saber el tipo de categoría del artículo y obtener dicho artículo
    if articulo.categoria == 'Ordenadores y Tablets':
        articulo = db.session.query(PC_Tablet).filter_by(id_articulo=int(id_articulo)).first()
        form = Form_pc_tablet(obj=articulo, id_articulo_actual=articulo.id_articulo)
        form.id_proveedor.choices = get_provedores()  # llamamos a la función get_proveedores()
        if form.validate_on_submit(): # si la validación es correcta actualizamos todos los campos
            try:
                articulo.referencia = form.referencia.data
                articulo.nombre = form.nombre.data
                articulo.marca = form.marca.data
                articulo.precio_venta = form.precio_venta.data
                articulo.stock = form.stock.data
                articulo.descripcion = form.descripcion.data
                articulo.ubicacion = form.ubicacion.data
                articulo.id_proveedor = form.id_proveedor.data
                articulo.precio_proveedor = form.precio_proveedor.data
                articulo.resolucion = form.resolucion.data
                articulo.procesador = form.procesador.data
                articulo.memoria = form.memoria.data
                articulo.almacenamiento = form.almacenamiento.data
                db.session.commit() # actualizamos datos en la base de datos
                # mensaje de exito para imprimir con 'flash messages' en el html
                flash('Artículo actualizado con éxito.', 'success')
                return redirect(url_for('articulo')) # redireccionamos a la función que nos carga de nuevo articulos.html

            except OperationalError: # gestionamos posible error de conexión con la base de datos
                db.session.rollback()
                flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
            except Exception: # gestionamos cualquier otro error
                db.session.rollback()
                flash('Error inesperado.', 'danger')

    # si el artículo es de esta categoría creamos un formulario Form_monitor
    elif articulo.categoria == 'Monitores':
        articulo = db.session.query(Monitor).filter_by(id_articulo=int(id_articulo)).first()
        form = Form_monitor(obj=articulo, id_articulo_actual=articulo.id_articulo)
        form.id_proveedor.choices = get_provedores()  # llamamos a la función get_proveedores()
        if form.validate_on_submit():
            try:
                articulo.referencia = form.referencia.data
                articulo.nombre = form.nombre.data
                articulo.marca = form.marca.data
                articulo.precio_venta = form.precio_venta.data
                articulo.stock = form.stock.data
                articulo.descripcion = form.descripcion.data
                articulo.ubicacion = form.ubicacion.data
                articulo.id_proveedor = form.id_proveedor.data
                articulo.precio_proveedor = form.precio_proveedor.data
                articulo.tamanio = form.tamanio.data
                articulo.resolucion = form.resolucion.data
                articulo.altura_ajustable = form.altura_ajustable.data
                articulo.conexiones = form.conexiones.data
                db.session.commit() # actualizamos datos en la base de datos
                # mensaje de exito para imprimir con 'flash messages' en el html
                flash('Artículo actualizado con éxito.', 'success')
                return redirect(url_for('articulo')) # redireccionamos a la función que nos carga de nuevo articulos.html

            except OperationalError: # gestionamos posible error de conexión con la base de datos
                db.session.rollback()
                flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
            except Exception: # gestionamos cualquier otro error
                db.session.rollback()
                flash('Error inesperado.', 'danger')

    # si el artículo es de esta categoría creamos un formulario Form_almacenamiento
    elif articulo.categoria == 'Almacenamiento':
        articulo = db.session.query(Almacenamiento).filter_by(id_articulo=int(id_articulo)).first()
        form = Form_almacenamiento(obj=articulo, id_articulo_actual=articulo.id_articulo)
        form.id_proveedor.choices = get_provedores()  # llamamos a la función get_proveedores()
        if form.validate_on_submit():
            try:
                articulo.referencia = form.referencia.data
                articulo.nombre = form.nombre.data
                articulo.marca = form.marca.data
                articulo.precio_venta = form.precio_venta.data
                articulo.stock = form.stock.data
                articulo.descripcion = form.descripcion.data
                articulo.ubicacion = form.ubicacion.data
                articulo.id_proveedor = form.id_proveedor.data
                articulo.precio_proveedor = form.precio_proveedor.data
                articulo.tipo = form.tipo.data
                articulo.capacidad = form.capacidad.data
                articulo.conexiones = form.conexiones.data
                db.session.commit() # actualizamos datos en la base de datos
                # mensaje de exito para imprimir con 'flash messages' en el html
                flash('Artículo actualizado con éxito.', 'success')
                return redirect(url_for('articulo')) # redireccionamos a la función que nos carga de nuevo articulos.html

            except OperationalError: # gestionamos posible error de conexión con la base de datos
                db.session.rollback()
                flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
            except Exception: # gestionamos cualquier otro error
                db.session.rollback()
                flash('Error inesperado.', 'danger')

    # si no el artículo será de la categoría Redes, por lo que creamos un formulario Form_redes
    else:
        articulo = db.session.query(Redes).filter_by(id_articulo=int(id_articulo)).first()
        form = Form_redes(obj=articulo, id_articulo_actual=articulo.id_articulo)
        form.id_proveedor.choices = get_provedores()  # llamamos a la función get_proveedores()
        if form.validate_on_submit():
            try:
                articulo.referencia = form.referencia.data
                articulo.nombre = form.nombre.data
                articulo.marca = form.marca.data
                articulo.precio_venta = form.precio_venta.data
                articulo.stock = form.stock.data
                articulo.descripcion = form.descripcion.data
                articulo.ubicacion = form.ubicacion.data
                articulo.id_proveedor = form.id_proveedor.data
                articulo.precio_proveedor = form.precio_proveedor.data
                articulo.tipo = form.tipo.data
                articulo.conexiones = form.conexiones.data
                db.session.commit() # actualizamos datos en la base de datos
                # mensaje de exito para imprimir con 'flash messages' en el html
                flash('Artículo actualizado con éxito.', 'success')
                return redirect(url_for('articulo')) # redireccionamos a la función que nos carga de nuevo articulos.html

            except OperationalError: # gestionamos posible error de conexión con la base de datos
                db.session.rollback()
                flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
            except Exception: # gestionamos cualquier otro error
                db.session.rollback()
                flash('Error inesperado.', 'danger')

    # obtenemos la lista de todos los proveedores para enviar al select del campo proveedor de crear-articulo.html
    form.id_proveedor.choices = get_provedores() # llamamos a la función get_proveedores()

    # renderizamos nuevamente la página editar-articulo.html en caso de error de validación del formulario...
    # ...o si no es una solicitud POST
    return render_template('editar-articulo.html', articulo=articulo, form=form)

# definimos ruta para acceder al listado de clientes paginados por parte del administrador
@app.route('/protected_admin/clientes', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/clientes?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def cliente(page, per_page):
    lista_clientes = db.session.query(Cliente).all() # extraemos todos los clientes de la base de datos
    total = len(lista_clientes)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL

    # extraemos el rango de artículos dependiendo de la página en la que estemos
    pagination_items = lista_clientes[offset:offset+per_page]

    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)

    # renderizamos la plantilla cliente facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('clientes.html', lista_clientes=pagination_items,
                           pagination=pagination)

@app.route('/protected_admin/clientes/crear_cliente', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_cliente(): # función que nos carga el template 'crear-cliente.html' y valida los datos del formulario
    form = Form_cliente() # instanciamos la clase Form_cliente
    # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
    if form.validate_on_submit():
        nombre = form.nombre.data
        nif = form.nif.data
        direccion = form.direccion.data
        contacto = form.contacto.data
        tlf_fijo = form.tlf_fijo.data
        tlf_movil = form.tlf_movil.data
        correo = form.correo.data
        forma_pago = form.forma_pago.data
        nuevo_cliente = Cliente(nombre, nif, direccion, contacto, tlf_fijo, tlf_movil, correo, forma_pago)
        # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
        if guardar_registro(nuevo_cliente):
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Nuevo cliente creado con éxito.', 'success')

            # Calculamos la última página después de añadir el cliente
            total_clientes = db.session.query(Cliente).count()
            per_page = 15  # Número de clientes por página (valor por defecto igual a 15)

            # Calculamos el número de la última página
            ultima_pagina = (total_clientes + per_page - 1) // per_page

            # redireccionamos a la función que nos carga de nuevo clientes.html
            return redirect(url_for('cliente', page=ultima_pagina, per_page=per_page))

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-cliente.html', form=form)

@app.route('/protected_admin/clientes/editar_cliente/<id_cliente>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'editar-cliente.html' a partir del id_cliente del cliente a editar
def editar_cliente(id_cliente):
    # obtenemos el cliente a editar a través de su id
    cliente = db.session.query(Cliente).filter_by(id_cliente=int(id_cliente)).first()
    form = Form_cliente(obj=cliente, id_cliente_actual=cliente.id_cliente)
    if form.validate_on_submit(): # si la validación es correcta actualizamos todos los campos
        try:
            cliente.nombre = form.nombre.data
            cliente.nif = form.nif.data
            cliente.direccion = form.direccion.data
            cliente.contacto = form.contacto.data
            cliente.tlf_fijo = form.tlf_fijo.data
            cliente.tlf_movil = form.tlf_movil.data
            cliente.correo = form.correo.data
            cliente.forma_pago = form.forma_pago.data
            db.session.commit() # actualizamos datos en la base de datos
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Cliente actualizado con éxito.', 'success')
            return redirect(url_for('cliente')) # redireccionamos a la función que nos carga de nuevo clientes.html
        except OperationalError: # gestionamos posible error de conexión con la base de datos
            db.session.rollback()
            flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
        except Exception: # gestionamos cualquier otro error
            db.session.rollback()
            flash('Error inesperado.', 'danger')

    # renderizamos nuevamente la página editar-cliente.html en caso de error de validación del formulario...
    # ...o si no es una solicitud POST
    return render_template('editar-cliente.html', cliente=cliente, form=form)

# definimos ruta para acceder al listado de proveedores paginados por parte del administrador
@app.route('/protected_admin/proveedores', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/proveedores?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def proveedor(page, per_page):
    lista_proveedores = db.session.query(Proveedor).all() # extraemos todos los proveedores de la base de datos
    total = len(lista_proveedores)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de proveedores dependiendo de la página en la que estemos
    pagination_items = lista_proveedores[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla cliente facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('proveedores.html', lista_proveedores=pagination_items,
                           pagination=pagination)

@app.route('/protected_admin/proveedores/crear_proveedor', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_proveedor(): # función que nos carga el template 'crear-proveedor.html' y valida los datos del formulario
    form = Form_proveedor() # instanciamos la clase Form_proveedor
    # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
    if form.validate_on_submit():
        nombre = form.nombre.data
        nif = form.nif.data
        direccion = form.direccion.data
        contacto = form.contacto.data
        tlf_fijo = form.tlf_fijo.data
        tlf_movil = form.tlf_movil.data
        correo = form.correo.data
        nuevo_proveedor = Proveedor(nombre, nif, direccion, contacto, tlf_fijo, tlf_movil, correo)
        # llamamos a la función guardar_registro para almacenar nuevo proveedor en la BBDD
        if guardar_registro(nuevo_proveedor):
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Nuevo proveedor creado con éxito.', 'success')

            # Calculamos la última página después de añadir el cliente
            total_proveedores = db.session.query(Proveedor).count()
            per_page = 15  # Número de proveedores por página (valor por defecto igual a 15)

            # Calculamos el número de la última página
            ultima_pagina = (total_proveedores + per_page - 1) // per_page

            # redireccionamos a la función que nos carga de nuevo proveedores.html
            return redirect(url_for('proveedor', page=ultima_pagina, per_page=per_page))

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-proveedor.html', form=form)

@app.route('/protected_admin/proveedores/detalle_proveedor/<id_proveedor>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'detalle-proveedor.html' del proveedor correspondiente cuando se solicita
def detalle_proveedor(id_proveedor):
    print(id_proveedor)
    # obtenemos el proveedor y sus artículos relacionados a través de su id
    proveedor = db.session.query(Proveedor).filter_by(id_proveedor=int(id_proveedor)).first()
    print(proveedor)
    articulos = db.session.query(Articulo).filter_by(id_proveedor=int(id_proveedor)).all()
    # cargamos el template con la información adicional del proveedor en cuestión
    return render_template('detalle-proveedor.html', lista_articulos=articulos, proveedor=proveedor)

@app.route('/protected_admin/proveedores/editar_proveedor/<id_proveedor>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'editar-proveedor.html' a partir del id_proveedor del proveedor a editar
def editar_proveedor(id_proveedor):
    # obtenemos el proveedor a editar a través de su id
    proveedor = db.session.query(Proveedor).filter_by(id_proveedor=int(id_proveedor)).first()
    form = Form_proveedor(obj=proveedor, id_proveedor_actual=proveedor.id_proveedor)
    if form.validate_on_submit(): # si la validación es correcta actualizamos todos los campos
        try:
            proveedor.nombre = form.nombre.data
            proveedor.nif = form.nif.data
            proveedor.direccion = form.direccion.data
            proveedor.contacto = form.contacto.data
            proveedor.tlf_fijo = form.tlf_fijo.data
            proveedor.tlf_movil = form.tlf_movil.data
            proveedor.correo = form.correo.data
            db.session.commit() # actualizamos datos en la base de datos
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Proveedor actualizado con éxito.', 'success')
            return redirect(url_for('proveedor')) # redireccionamos a la función que nos carga de nuevo proveedores.html

        except OperationalError: # gestionamos posible error de conexión con la base de datos
            db.session.rollback()
            flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
        except Exception: # gestionamos cualquier otro error
            db.session.rollback()
            flash('Error inesperado.', 'danger')

    # renderizamos nuevamente la página editar-proveedor.html en caso de error de validación del formulario...
    # ...o si no es una solicitud POST
    return render_template('editar-proveedor.html', proveedor=proveedor, form=form)

@app.route('/protected_admin/<area>/confirmar_eliminar/<id_registro>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# función que carga la plantilla confirmar-eliminar-{area}.html y nos muestra el registro a eliminar
def confirmar_eliminar(area, id_registro):
    form = Form_eliminar_registro() # inicializamos el formulario WFT
    # creamos un diccionario con la clave 'area' y el correspondiente modelo
    modelos = {
        'proveedor': Proveedor,
        'articulo': Articulo,
        'cliente': Cliente,
        'venta': Venta,
        'pedido': Pedido,
        'usuario': User
    }
    modelo = modelos.get(area) # obtenemos el modelo correspondiente al área en cuestión
    registro = db.session.get(modelo, id_registro) # extraemos el registro a eliminar
    # renderizamos la plantilla correspondiente según el área
    return render_template(f'confirmar-eliminar-{area}.html', registro=registro, form=form)


@app.route('/protected_admin/<area>/eliminar_registro/<id_registro>', methods=['POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# función que elimina el registro seleccionado y nos devuelve a la área correspondiente según el tipo de registro
def eliminar_registro(area, id_registro):
    modelos = {
        'proveedor': Proveedor,
        'articulo': Articulo,
        'cliente': Cliente,
        'venta': Venta,
        'pedido': Pedido,
        'usuario': User
        }
    modelo = modelos.get(area)
    try:
        if area == 'venta':
            # Recuperamos los detalles de la venta antes de eliminarlos para poder actualizar el stock
            detalles = db.session.query(Detalle_venta).filter_by(id_venta=id_registro).all()
            for detalle in detalles:
                articulo = db.session.query(Articulo).get(detalle.id_articulo)
                if articulo:
                    articulo.stock += detalle.cantidad  # Reponemos el stock
        elif area == 'pedido':
            # Recuperamos los detalles del pedido antes de eliminarlos para poder actualizar el stock
            detalles = db.session.query(Detalle_pedido).filter_by(id_pedido=id_registro).all()
            for detalle in detalles:
                articulo = db.session.query(Articulo).get(detalle.id_articulo)
                if articulo:
                    articulo.stock -= detalle.cantidad  # Descontamos del stock

        registro = db.session.get(modelo, id_registro) # extraemos el registro a eliminar
        db.session.delete(registro) # eliminamos registro
        db.session.commit()
        flash(f'{modelo.__name__} eliminado con éxito.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar el registro.', 'danger')
    return redirect(url_for(area)) # redireccionamos a la función correspondiente dependiendo del 'area'


# definimos ruta para acceder al listado de ventas paginados por parte del administrador
@app.route('/protected_admin/ventas', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/ventas?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def venta(page, per_page):
    lista_ventas = db.session.query(Venta).all() # extraemos todos las ventas de la base de datos
    total = len(lista_ventas)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de ventas dependiendo de la página en la que estemos
    pagination_items = lista_ventas[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla ventas.html facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('ventas.html', lista_ventas=pagination_items, pagination=pagination)

@app.route('/protected_admin/ventas/detalle_venta/<id_venta>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'detalle-venta.html' de la venta correspondiente cuando se solicita
def detalle_venta(id_venta):
    # obtenemos la venta seleccionada a través de su id
    venta = db.session.query(Venta).filter_by(id_venta=int(id_venta)).first()
    # cargamos el template con la información adicional de venta en cuestión
    return render_template('detalle-venta.html', venta=venta)

@app.route('/protected_admin/ventas/crear_venta', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_venta(): # función que nos carga el template 'crear-venta.html' y valida los datos del formulario
    form = Form_venta() # instanciamos la clase Form_venta y cargamos la fecha de creación de la venta
    # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
    if form.validate_on_submit():
        id_cliente = form.id_cliente.data
        fecha = date.today()
        impuesto = form.impuesto.data
        nueva_venta = Venta(id_cliente=id_cliente, fecha=fecha, impuesto=impuesto, total_neto=0, total=0)
        # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
        if guardar_registro(nueva_venta):
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Nueva venta creada con éxito.', 'success')
            # redireccionamos a la función que nos carga de nuevo add-articulo.html y le pasamos el id de la venta
            return redirect(url_for('add_articulo', id_venta=nueva_venta.id_venta))
    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-venta.html', form=form)

@app.route('/buscar_cliente', methods=['GET']) # ruta que acepta solicitudes de búsqueda (peticiones GET)
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# función usada por API Fetch de javascript dentro de la plantilla crear-venta.html que busca en base de datos...
# ...los clientes según el criterio de búsqueda introducido en el campo cliente.
def buscar_cliente():
    term = request.args.get('term', '') # toma el parámetro 'term' de la consulta (lo que el usuario ha escrito)
    clientes = db.session.query(Cliente).filter(Cliente.nombre.ilike(f'%{term}%')).all() # obtiene los clientes que coinciden
    # recorremos la lista de objetos clientes y extraemos su id y nombre y los almacemos como una lista de diccionarios
    resultados = [{'id': cliente.id_cliente, 'nombre': cliente.nombre} for cliente in clientes]
    return jsonify(resultados) # devuelve la lista de clientes en formato json usando la función jsonfy de Flask


@app.route('/protected_admin/crear_venta/add_articulo/<id_venta>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def add_articulo(id_venta):
    venta = db.session.get(Venta, id_venta)
    form = Form_add_articulo()
    form.es_pedido = False # indicamos al formulario que se trata de una venta (no es un pedido)
    if form.validate_on_submit():
        id_articulo = form.id_articulo.data
        cantidad = form.cantidad.data
        articulo = db.session.query(Articulo).get(id_articulo)
        try:
            # Creamos Detalle_venta
            detalle_venta = Detalle_venta(id_venta=id_venta, id_articulo=id_articulo, cantidad=cantidad)
            db.session.add(detalle_venta)
            # Actualizamos stock del artículo
            articulo.stock -= cantidad
            # Actualizamos total neto de la venta redondeando a 2 decimales
            venta.total_neto += round((cantidad * articulo.precio_venta), 2)
            # Actualizamos total de la venta redondeando a 2 decimales
            venta.total = round((venta.total_neto * (1 + venta.impuesto)), 2)
            db.session.commit()
            flash('Artículo agregado exitosamente a la venta.', 'success')
            # Redirigimos nuevamente a add_articulo para enviar el reenvío del formulario en caso de actualizar la página
            return redirect(url_for('add_articulo', id_venta=id_venta))
        except Exception:
            db.session.rollback() # deshacemos cambios en caso de error
            flash('Error al agregar artículo a la venta.', 'danger')
    # Obtenemos los artículos relacionados en el detalle de la venta actual para poder mostrarlos y actualizalo...
    #...cada vez que añadimos un artículo
    articulos = db.session.query(Detalle_venta).join(Articulo).filter(Detalle_venta.id_venta == id_venta).all()
    return render_template('add-articulo.html', form=form, venta=venta, articulos=articulos)

@app.route('/buscar_articulo', methods=['GET'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# función usada por API Fetch de javascript dentro de la plantilla add-articulo.html que busca en base de datos...
# ...los articulos según el criterio de búsqueda introducido en el campo ya sea por referencia o nombre del artículo.
def buscar_articulo():
    term = request.args.get('term', '').strip() # la función strip elimina los caracteres de inicio o fin de línea sobrantes
    id_proveedor = request.args.get('id_proveedor', type=int)
    resultados = []
    if term:
        # Consulta que busca por referencia o nombre el artículo
        articulos = db.session.query(Articulo).filter(
            (Articulo.referencia.ilike(f'%{term}%')) | (Articulo.nombre.ilike(f'%{term}%'))
            )
        # En caso de recibir id_proveedor (para Pedidos) filtramos por el id_proveedor
        if id_proveedor:
            articulos = articulos.filter(Articulo.id_proveedor == id_proveedor)

        articulos = articulos.all()
        resultados = [{'id': articulo.id_articulo, 'nombre': articulo.nombre, 'referencia': articulo.referencia}
                      for articulo in articulos]
    return jsonify(resultados)

@app.route('/protected_admin/crear_venta/eliminar_articulo/<id_detalle_venta>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos eliminar el artículo seleccionado de la venta
def eliminar_articulo_venta(id_detalle_venta):
    try:
        # Accedemos al detalle de la venta a eliminar
        detalle_venta = db.session.query(Detalle_venta).filter_by(id_detalle_venta=id_detalle_venta).first()
        # Actualizamos stock del artículo eliminado de la venta
        detalle_venta.rel_articulo.stock += detalle_venta.cantidad
        # Obtenemos la venta actual para actualizar sus datos
        venta = db.session.query(Venta).filter_by(id_venta=detalle_venta.id_venta).first()
        # Actualizamos total neto de la venta redondeando a 2 decimales
        venta.total_neto -= round((detalle_venta.cantidad * detalle_venta.rel_articulo.precio_venta), 2)
        # Actualizamos total de la venta redondeando a 2 decimales
        venta.total = round(venta.total_neto * (1 + venta.impuesto), 2)
        # Extraemos el id_venta antes de borrar el detalle de venta, para poder redireccionar al final a 'add_articulo'
        id_venta = detalle_venta.id_venta
        # Eliminamos el detalle de venta seleccionado
        db.session.query(Detalle_venta).filter_by(id_detalle_venta=id_detalle_venta).delete()
        db.session.commit()
        # mensaje de exito para imprimir con 'flash messages' en el html
        flash('Artículo eliminado con éxito de la venta.', 'success')
        # redireccionamos a la función que nos carga de nuevo add-articulo.html actualizado
        return redirect(url_for('add_articulo', id_venta=id_venta))
    except Exception:
        db.session.rollback()  # deshacemos cambios en caso de error
        flash('Error al eliminar artículo de la venta.', 'danger')
        # en caso de error redireccionamos a la función que nos carga de nuevo ventas.html
        return redirect(url_for('venta'))

# definimos ruta para acceder al listado de pedidos paginados por parte del administrador
@app.route('/protected_admin/pedidos', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/pedidos?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def pedido(page, per_page):
    lista_pedidos = db.session.query(Pedido).all() # extraemos todos los pedidos de la base de datos
    total = len(lista_pedidos)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de pedidos dependiendo de la página en la que estemos
    pagination_items = lista_pedidos[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla pedidos.html facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('pedidos.html', lista_pedidos=pagination_items, pagination=pagination)

@app.route('/protected_admin/pedidos/detalle_pedido/<id_pedido>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'detalle-pedido.html' del pedido correspondiente cuando se solicita
def detalle_pedido(id_pedido):
    # obtenemos el pedido seleccionada a través de su id
    pedido = db.session.query(Pedido).filter_by(id_pedido=int(id_pedido)).first()
    # cargamos el template con la información adicional del pedido en cuestión
    return render_template('detalle-pedido.html', pedido=pedido)

@app.route('/protected_admin/pedidos/crear_pedido', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_pedido(): # función que nos carga el template 'crear-pedido.html' y valida los datos del formulario
    form = Form_pedido() # instanciamos la clase Form_pedido y cargamos la fecha de creación del pedido
    # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
    if form.validate_on_submit():
        id_proveedor = form.id_proveedor.data
        fecha = date.today()
        impuesto = form.impuesto.data
        nueva_pedido = Pedido(id_proveedor, fecha, total_neto=0, impuesto=impuesto, total=0)

        # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
        if guardar_registro(nueva_pedido):
            # mensaje de éxito para imprimir con 'flash messages' en el html
            flash('Nueva pedido creado con éxito.', 'success')
            # redireccionamos a la función que nos carga de nuevo add-articulo.html y le pasamos el id del pedido
            return redirect(url_for('get_articulo', id_pedido=nueva_pedido.id_pedido))

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-pedido.html', form=form)

@app.route('/buscar_proveedor', methods=['GET']) # ruta que acepta solicitudes de búsqueda (peticiones GET)
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# función usada por API Fetch de javascript dentro de la plantilla crear-pedido.html que busca en base de datos...
# ...los proveedores según el criterio de búsqueda introducido en el campo proveedor.
def buscar_proveedor():
    term = request.args.get('term', '') # toma el parámetro 'term' de la consulta (lo que el usuario ha escrito)
    proveedores = db.session.query(Proveedor).filter(Proveedor.nombre.ilike(f'%{term}%')).all() # obtiene los proveedores que coinciden
    # recorremos la lista de objetos proveedores y extraemos su id y nombre y los almacemos como una lista de diccionarios
    resultados = [{'id': proveedor.id_proveedor, 'nombre': proveedor.nombre} for proveedor in proveedores]
    return jsonify(resultados) # devuelve la lista de proveedores en formato json usando la función jsonfy de Flask

@app.route('/protected_admin/crear_pedido/get_articulo/<id_pedido>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def get_articulo(id_pedido):
    pedido = db.session.get(Pedido, id_pedido)
    form = Form_add_articulo()
    # Indicamos que el formulario es para un pedido, para que no tenga en cuenta el validador de stock
    form.es_pedido = True
    if form.validate_on_submit():
        id_articulo = form.id_articulo.data
        cantidad = form.cantidad.data
        articulo = db.session.query(Articulo).get(id_articulo)
        try:
            # Creamos Detalle_pedido
            detalle_pedido = Detalle_pedido(id_pedido=id_pedido, id_articulo=id_articulo, cantidad=cantidad)
            db.session.add(detalle_pedido)
            # Actualizamos stock del artículo
            articulo.stock += cantidad
            # Actualizamos total neto del pedido redondeando a 2 decimales
            pedido.total_neto += round((cantidad * articulo.precio_proveedor), 2)
            # Actualizamos total del pedido redondeando a 2 decimales
            pedido.total = round((pedido.total_neto * (1 + pedido.impuesto)), 2)
            db.session.commit()
            flash('Artículo agregado exitosamente al pedido.', 'success')

            # Redirigimos nuevamente a add_articulo para enviar el reenvío del formulario en caso de actualizar la página
            return redirect(url_for('get_articulo', id_pedido=id_pedido))
        except Exception:
            db.session.rollback() # deshacemos cambios en caso de error
            flash('Error al agregar artículo al pedido.', 'danger')

    # Obtenemos los artículos relacionados en el detalle del pedido actual para poder mostrarlos y actualizalo...
    #...cada vez que añadimos un artículo
    articulos = db.session.query(Detalle_pedido).join(Articulo).filter(Detalle_pedido.id_pedido == id_pedido).all()
    return render_template('get-articulo.html', form=form, pedido=pedido, articulos=articulos)

@app.route('/protected_admin/crear_pedido/eliminar_articulo/<id_detalle_pedido>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que elimina el articulo seleccionado de un pedido
def eliminar_articulo_pedido(id_detalle_pedido):
    try:
        # Accedemos al detalle del pedido a eliminar
        detalle_pedido = db.session.query(Detalle_pedido).filter_by(id_detalle_pedido=id_detalle_pedido).first()
        # Actualizamos stock del artículo eliminado del pedido
        detalle_pedido.rel_pedido_articulo.stock -= detalle_pedido.cantidad
        # Obtenemos el pedido actual para actualizar sus datos
        pedido = db.session.query(Pedido).filter_by(id_pedido=detalle_pedido.id_pedido).first()
        # Actualizamos total neto del pedido redondeando a 2 decimales
        pedido.total_neto -= round((detalle_pedido.cantidad * detalle_pedido.rel_pedido_articulo.precio_proveedor), 2)
        # Actualizamos total del pedido redondeando a 2 decimales
        pedido.total = round(pedido.total_neto * (1 + pedido.impuesto), 2)

        # Extraemos el id_pedido antes de borrar el detalle de pedido, para poder redireccionar al final a 'get_articulo'
        id_pedido = detalle_pedido.id_pedido
        # Eliminamos el detalle de pedido seleccionado
        db.session.query(Detalle_pedido).filter_by(id_detalle_pedido=id_detalle_pedido).delete()
        db.session.commit()
        # mensaje de exito para imprimir con 'flash messages' en el html
        flash('Artículo eliminado con éxito del pedido.', 'success')

        # redireccionamos a la función que nos carga de nuevo get-articulo.html actualizado
        return redirect(url_for('get_articulo', id_pedido=id_pedido))
    except Exception:
        db.session.rollback()  # deshacemos cambios en caso de error
        flash('Error al eliminar artículo del pedido.', 'danger')
        # en caso de error redireccionamos a la función que nos carga de nuevo pedidos.html
        return redirect(url_for('pedido'))

@app.route('/protected_admin/nuevo_analisis', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def nuevo_analisis(): # función que nos carga el template 'nuevo-analisis.html' y valida los datos del formulario
    form = Form_analisis() # instanciamos la clase Form_analisis
    # validamos que no haya errores en el registro de datos del formulario
    if form.validate_on_submit():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        modelo = form.modelo.data
        periodicidad = form.periodicidad.data
        # llamamos a la función analisis_financiero facilitándoles los parámetros de la consulta (fechas y modelo) y...
        # ...esta nos devuelve la ruta donde se ha almacenado nuestro gráfico y el dataframe con los datos
        img_path, df_analisis = analisis_financiero(
                fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, periodicidad=periodicidad, modelo=modelo)
        #convertiamos el dataframe en una lista de diccionarios
        datos_grafico = df_analisis.to_dict(orient='records')

        # renderizamos la página para mostrar el gráfico facilitándole la ruta contenida en 'img_path' y sus datos para...
        # ...para poder mostrarlos en una tabla
        if modelo == 'Beneficio': # para beneficio
            print(datos_grafico)

            return render_template('analisis-beneficios.html',
                                   img_path=img_path, datos_grafico=datos_grafico, modelo=modelo)
        else: # para ventas o pedidos
            return render_template('analisis-ventas-pedidos.html',
                                   img_path=img_path, datos_grafico=datos_grafico, modelo=modelo)

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('nuevo-analisis.html', form=form)

# definimos ruta para acceder al listado de usuarios paginados por parte del administrador
@app.route('/protected_admin/usuarios', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected_admin/usuarios?page=<int:page>?per_page=<int:per_page>')
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def usuario(page, per_page):
    lista_usuario = db.session.query(User).all() # extraemos todos los usuarios de la base de datos
    total = len(lista_usuario)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de usuarios dependiendo de la página en la que estemos
    pagination_items = lista_usuario[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla usuarios.html facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('usuarios.html', lista_usuarios=pagination_items, pagination=pagination)

@app.route('/protected_admin/usuarios/crear_usuario', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
def crear_usuario(): # función que nos carga el template 'crear-usuario.html' y valida los datos del formulario
    form = Form_usuario() # instanciamos la clase Form_usuario
    # validamos que no haya errores en el registro de datos del formulario y en tal caso registramos los datos
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        password = generate_password_hash(password) # encriptamos la contraseña
        type_user = bool(int(form.type_user.data))
        nuevo_usuario = User(username, password, type_user)
        # llamamos a la función guardar_registro para almacenar nuevo_articulo en la BBDD
        if guardar_registro(nuevo_usuario):
        # si no hay error al guardar el registro imprimimos mensaje de éxito con 'flash messages' en el html
            flash('Nuevo usuario creado con éxito.', 'success')
            return redirect(url_for('usuario')) # redireccionamos a la función que nos carga de nuevo usuarios.html

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('crear-usuario.html', form=form)

@app.route('/protected_admin/usuarios/editar_usuario/<id>', methods=['GET', 'POST'])
@login_required
@admin_required # Vista protegida que solo se puede acceder con autenticación de administrador
# funcion que nos carga el template 'editar-usuario.html' a partir del id del usuario a editar
def editar_usuario(id):
    # obtenemos el usuario a editar a través de su id
    usuario = db.session.query(User).filter_by(id=int(id)).first()
    form = Form_usuario(obj=usuario, id_usuario_actual=usuario.id)
    if form.validate_on_submit(): # si la validación es correcta actualizamos todos los campos
        try:
            usuario.username = form.username.data
            usuario.password = generate_password_hash(form.password.data)
            usuario.type_user = bool(int(form.type_user.data))
            db.session.commit() # actualizamos datos en la base de datos
            # mensaje de exito para imprimir con 'flash messages' en el html
            flash('Usuario actualizado con éxito.', 'success')
            return redirect(url_for('usuario')) # redireccionamos a la función que nos carga de nuevo usuarios.html

        except OperationalError: # gestionamos posible error de conexión con la base de datos
            db.session.rollback()
            flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
        except Exception: # gestionamos cualquier otro error
            db.session.rollback()
            flash('Error inesperado.', 'danger')

    # renderizamos nuevamente la página editar-cliente.html en caso de error de validación del formulario...
    # ...o si no es una solicitud POST
    # redireccionamos a la función que nos carga de nuevo clientes.html actualizado
    return render_template('editar-usuario.html', usuario=usuario, form=form)


#####---------------------------------RUTAS DE ACCESO DE USUARIO TIPO CLIENTE-------------------------------------######
@app.route('/protected/mi_cuenta', methods=['GET','POST'])
@login_required
# funcion que nos carga el template 'mi-cuenta.html' que muestra la información del usuario
def mi_cuenta():
    # obtenemos el cliente identificado a través de su nif
    cliente = db.session.query(Cliente).filter_by(nif=current_user.username).first()
    # cargamos el template con la información de la cuenta del cliente
    form = Form_update_pass()
    if form.validate_on_submit(): # validamos el formulario
        user = db.session.query(User).get(current_user.id) # obtenemos usuario actual
        user.set_password(form.new_pass.data) # llámamos al método de la clase User para establecer nueva contraseña
        db.session.commit() # envíamos cambio a la base de datos
        flash('Contraseña actualizada con éxito.', 'success')
        return redirect(url_for('mi_cuenta'))
    return render_template('mi-cuenta.html', cliente=cliente, form=form)

# definimos ruta para acceder al listado de ventas paginados por parte del administrador
@app.route('/protected/mis_compras', methods=['GET'], defaults={'page':1, 'per_page':15})
@app.route('/protected/mis_compras?page=<int:page>?per_page=<int:per_page>')
@login_required
def mis_compras(page, per_page):
    cliente = db.session.query(Cliente).filter_by(nif=current_user.username).first()
    # extraemos todos las ventas de la base de datos
    lista_ventas = db.session.query(Venta).filter_by(id_cliente=cliente.id_cliente).all()
    total = len(lista_ventas)
    page, per_page, offset = get_page_args() # método para extraer los parámetros de paginación de una URL
    # extraemos el rango de ventas dependiendo de la página en la que estemos
    pagination_items = lista_ventas[offset:offset+per_page]
    # usamos la clase Pagination de Flask-Paginate facilitando los parámetros de paginación
    pagination = Pagination(page=page, total=total, per_page=per_page)
    # renderizamos la plantilla mis-compras.html facilitándole  el rango de datos a mostrar y los parámetros de paginación
    return render_template('mis-compras.html', lista_ventas=pagination_items, pagination=pagination)

@app.route('/protected/mis_compras/detalle_compra/<id_venta>')
@login_required
# funcion que nos carga el template 'detalle-venta.html' para el acceso de usuario tipo cliente
def detalle_compra(id_venta):
    # obtenemos la venta seleccionada a través de su id y nos aseguramos de que el cliente coincide...
    # ...con el usuario logueado para evitar accesos no deseados a otras rutas a través de la url
    cliente = current_user.get_cliente()
    venta = db.session.query(Venta).filter_by(id_venta=int(id_venta), id_cliente=cliente.id_cliente).first()
    if not venta:
        flash('No tienes permiso para acceder a esta ruta.', 'danger')
        return redirect(url_for('protected'))

    # cargamos el template con la información adicional de venta en cuestión
    return render_template('detalle-compra.html', venta=venta)

@app.route('/protected/nuevo_analisis_compras', methods=['GET', 'POST'])
@login_required
def nuevo_analisis_compras(): # función que nos carga el template 'nuevo-analisis-cliente.html' y valida los datos del formulario
    form = Form_analisis_cliente() # instanciamos la clase Form_analisis_cliente
    # validamos que no haya errores en el registro de datos del formulario
    if form.validate_on_submit():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        periodicidad = form.periodicidad.data

        cliente = db.session.query(Cliente).filter_by(nif=current_user.username).first()
        id_cliente = cliente.id_cliente
        # llamamos a la función analisis_financiero facilitándoles los parámetros de la consulta y...
        # ...esta nos devuelve la ruta donde se ha almacenado nuestro gráfico y el dataframe
        img_path, df_analisis = analisis_financiero(
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, periodicidad=periodicidad, id_cliente=id_cliente)
        #convertiamos el dataframe en una lista de diccionarios
        datos_grafico = df_analisis.to_dict(orient='records')

        # renderizamos la página para mostrar el gráfico facilitándole la ruta contenida en 'img_path' y sus datos para...
        # ...para poder mostrarlos en una tabla
        return render_template('analisis-compras.html',
                                   img_path=img_path, datos_grafico=datos_grafico)

    # si no existe una validación correcta de los datos del formulario, renderizamos la página nuevamente mostrando errores
    return render_template('nuevo-analisis-cliente.html', form=form)


if __name__ == '__main__':
    # indicamos a SQLAlchemy que cree si no existen ya las tablas de todos los modelos
    db.Base.metadata.create_all(bind=db.engine)
    app.run(debug=True) # iniciamos el servidor web

