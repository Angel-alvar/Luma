from flask import (
    Flask, render_template, redirect, url_for, request, 
    jsonify, flash, abort
)
from models import db, Usuario, Empleado, Cliente, Producto, Insumo, Pedido, DetallePedido, SeguimientoPedido
from flask_mail import Mail, Message
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:muffin@localhost/luma')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inicializar la base de datos
db.init_app(app)
with app.app_context():
    db.create_all()
    print("Base de datos creada.")


# Rutas principales
@app.route('/')
def raiz():
    return redirect(url_for('inicio'))

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/acerca')
def acerca():   
    return render_template('acerca.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')


if __name__ == '__main__':
    app.run(debug=True)
    app.config['DEBUG'] = True
    
    