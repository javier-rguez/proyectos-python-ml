import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# El engine permite a SQLAlchemy comunicarse con la base de datos
#https://docs.sqlalchemy.org/en/14/core/engines.html
engine = create_engine('sqlite:///database/SuministrosInformaticos.db',
                       connect_args={'check_same_thread': False})

# Habilitamos el soporte de claves foráneas en SQLite en cada sesión
@event.listens_for(engine, 'connect')
def enable_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON;')  # Habilitar claves foráneas
        cursor.close()

# Ahora crearemos la sesión, lo que nos permite realizar transacciones dentro de la bd
Session = sessionmaker(bind=engine)
session = Session()

# Creación de la clase Base para conectar nuestros modelos (clases)...
#...y mapear esa información a tablas en nuestra base de datos
Base = declarative_base()