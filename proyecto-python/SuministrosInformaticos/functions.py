import os

from sqlalchemy.exc import OperationalError

import db
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash
from models import Proveedor

# definimos un decorador personalizado para proteger las rutas de administrador
def admin_required(f): # recibe como parámetro una función 'f' que será la función a proteger
    @wraps(f)
    def decorated_function(*args, **kwargs): # verificamos si el usuario está autentificado
        # si el usuario no tiene permiso de acceso a la ruta se le deniega el acceso
        if not current_user.is_authenticated or not current_user.type_user:
            flash('Acceso denegado. Solo los administradores pueden acceder a la ruta introducida.',
                  'danger')
            return redirect(url_for('protected'))
        return f(*args, **kwargs) # si el usuario está logueado y es administrador ejecuta la función 'f'
    return decorated_function

def get_provedores():
    '''Función que nos devuelve una lista de tuplas con el 'id_proveedor' y el 'nombre' del proveedor'''
    proveedores = db.session.query(Proveedor).all()
    lista_proveedores = []  # inicializamos una lista de opciones vacía
    # recorremos la lista 'proveedores' de objetos proveedor y extraemos id_proveedor y nombre y la almacenamos...
    # ...como una tupla dentro de 'lista_proveedores'
    for proveedor in proveedores:
        lista_proveedores.append((proveedor.id_proveedor, proveedor.nombre))
    return lista_proveedores

def guardar_registro(registro):
    '''funcion que recibe un nuevo registro y lo almacena en la base de datos'''
    try: # capturamos errores durante el registro de datos en la base de datos
        db.session.add(registro) # añadimos nuevo registro a la base de datos
        db.session.commit()
        return True # éxito al guardar el registro
    except OperationalError:  # gestionamos posible error de conexión con la base de datos
        db.session.rollback()
        flash('Error de comunicación con la base de datos. Inténtalo más tarde.', 'danger')
    except Exception as e:
        db.session.rollback() # revertimos los cambios en caso de error
        flash(f'Error inesperado: {e} .', 'danger')
        return False # error al guardar el registro

def analisis_financiero(fecha_inicio, fecha_fin, periodicidad, modelo=None, id_cliente=None):
# función que retorna el gráfico y el dataframe de la consulta realizada
    # evita el error al generar gráficos en entornos que no permiten la inicialización de ventanas fuera del hilo ppal
    matplotlib.use('Agg') # establecemos un backend no interactivo

    if id_cliente == None:
        if modelo == 'Beneficio':
            if periodicidad == 'mensual':
                # Consulta SQL para obtener los datos según los criterios de búsqueda introducidos en el formulario
                # Consulta para periodicidad mensual
                query = f"""
                            SELECT 
                                strftime('%m-%Y', v.fecha) AS periodicidad,
                                COALESCE(SUM(v.total), 0) AS ingresos,
                                COALESCE(SUM(p.total), 0) AS gastos,
                                COALESCE(SUM(v.total), 0) - COALESCE(SUM(p.total), 0) AS beneficios,
                                CAST(strftime('%Y', v.fecha) AS INTEGER) * 100 + CAST(strftime('%m', v.fecha) AS INTEGER) AS orden
                            FROM Venta v
                            LEFT JOIN Pedido p ON strftime('%m-%Y', v.fecha) = strftime('%m-%Y', p.fecha)
                            WHERE v.fecha BETWEEN :fecha_inicio AND :fecha_fin OR p.fecha BETWEEN :fecha_inicio AND :fecha_fin
                            GROUP BY periodicidad
                            ORDER BY orden
                        """
            else:
                # Consulta SQL para obtener datos según los criterios de búsqueda introducidos en el formulario
                # Consulta para periodicidad anual
                query = f"""
                            SELECT 
                                strftime('%Y', v.fecha) AS periodicidad,
                                COALESCE(SUM(v.total), 0) AS ingresos,
                                COALESCE(SUM(p.total), 0) AS gastos,
                                COALESCE(SUM(v.total), 0) - COALESCE(SUM(p.total), 0) AS beneficios
                            FROM Venta v
                            LEFT JOIN Pedido p ON strftime('%Y', v.fecha) = strftime('%Y', p.fecha)
                            WHERE v.fecha BETWEEN :fecha_inicio AND :fecha_fin OR p.fecha BETWEEN :fecha_inicio AND :fecha_fin
                            GROUP BY periodicidad
                            ORDER BY periodicidad
                    """
        else:
            if periodicidad == 'mensual':
                # Consulta SQL para obtener los datos según los criterios de búsqueda introducidos en el formulario
                # Consulta para periodicidad mensual
                query = f"""
                            SELECT strftime('%m-%Y', fecha) AS periodicidad, 
                                SUM(total) AS total,
                                CAST(strftime('%Y', fecha) AS INTEGER) * 100 + CAST(strftime('%m', fecha) AS INTEGER) AS orden
                            FROM {modelo}
                            WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin
                            GROUP BY periodicidad
                            ORDER BY orden
                        """
            else:
                # Consulta SQL para obtener datos según los criterios de búsqueda introducidos en el formulario
                # Consulta para periodicidad anual
                query = f"""
                            SELECT strftime('%Y', fecha) AS periodicidad, 
                                SUM(total) AS total
                            FROM {modelo}
                            WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin
                            GROUP BY periodicidad
                            ORDER BY periodicidad
                    """
        # pasamos los parámetros de las fechas como un diccionario para que sean reconocidos en la consulta sql
        params = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
    else:
        if periodicidad == 'mensual':
            # Consulta SQL para obtener los datos según los criterios de búsqueda introducidos en el formulario
            # Consulta para periodicidad mensual
            query = f"""
                        SELECT strftime('%m-%Y', fecha) AS periodicidad, 
                            SUM(total) AS total,
                            CAST(strftime('%Y', fecha) AS INTEGER) * 100 + CAST(strftime('%m', fecha) AS INTEGER) AS orden
                        FROM Venta
                        WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin AND id_cliente = :id_cliente
                        GROUP BY periodicidad
                        ORDER BY orden
                        """
        else:
            # Consulta SQL para obtener datos según los criterios de búsqueda introducidos en el formulario
            # Consulta para periodicidad anual
            query = f"""
                        SELECT strftime('%Y', fecha) AS periodicidad, 
                            SUM(total) AS total
                        FROM Venta
                        WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin AND id_cliente = :id_cliente
                        GROUP BY periodicidad
                        ORDER BY periodicidad
                    """
        # pasamos los parámetros de las fechas y el id_cliente como un diccionario para que sean reconocidos en la consulta sql
        params = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin, 'id_cliente': id_cliente}

    try: # capturamos errores durante la consulta a la base de datos para obtener el dataframe
        # obtenemos dataframe utilizando Pandas con el que generaremos el gráfico
        df_analisis = pd.read_sql_query(query, db.engine, params=params)
    except Exception as e:
        flash(f'Error al ejecutar la consulta a la base de datos: {e}', 'danger')
        return None, None # retornamos valores indicativos de error para poder tratarlos en el main.py

    # Creamos gráfico estableciendo sus características dependiendo del modelo seleccionado
    if modelo == 'Beneficio':
        # Transformamos los datos del dataframe para adaptarlo para un gráficio de barras agrupadas
        df_modificado = df_analisis.melt(id_vars='periodicidad',
                                     value_vars=['ingresos', 'gastos', 'beneficios'],
                                     var_name='Categoría', value_name='Total')
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_modificado, x='periodicidad', y='Total', hue='Categoría', palette='Blues_d')
    else:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_analisis, x='periodicidad', y='total', color='skyblue')
        if id_cliente is not None:
            plt.title('Compras en el periodo seleccionado'.format(modelo))
        else:
            plt.title('{}s en el periodo seleccionado'.format(modelo))

    plt.xlabel('Periodicidad: {}'.format(periodicidad))
    plt.ylabel('Cantidad (€)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardamos gráfico en el directorio static/images
    img_path = os.path.join('static', 'images', 'analisis.png')
    plt.savefig(img_path)
    plt.close()  # Cerramos la figura para liberar memoria
    # retornamos ruta del gráfico y dataframe
    return img_path, df_analisis