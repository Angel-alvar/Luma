from flask import (
    Flask, render_template, redirect, url_for, request, 
    jsonify, flash, abort
)
from models import db, Usuario, TipoUsuario, Empleado, Cliente, Producto, Insumo, Pedido, DetallePedido, SeguimientoPedido
from flask_mail import Mail, Message
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
from functools import wraps
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de base de datos con ruta absoluta para mariadb

app.config ['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:muffin@localhost/luma'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-desarrollo')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()






# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


def empleado_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_empleado:
            flash('Acceso denegado. Se requieren permisos de empleado.', 'danger')
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


def init_database():
    """Inicializa la base de datos con tipos de usuario por defecto"""
    db.create_all()
    
    # Crear tipos de usuario si no existen
    tipos_default = [
        {'nombre': 'admin', 'descripcion': 'Administrador del sistema'},
        {'nombre': 'empleado', 'descripcion': 'Empleado de la empresa'},
        {'nombre': 'cliente', 'descripcion': 'Cliente registrado'}
    ]
    
    for tipo_data in tipos_default:
        tipo = TipoUsuario.query.filter_by(nombre=tipo_data['nombre']).first()
        if not tipo:
            tipo = TipoUsuario(**tipo_data)
            db.session.add(tipo)
    
    db.session.commit()
    
    # Crear usuario admin por defecto si no existe
    # La contraseña del admin se toma de variable de entorno o usa valor por defecto
    admin_tipo = TipoUsuario.query.filter_by(nombre='admin').first()
    if admin_tipo:
        admin_user = Usuario.query.filter_by(correo='admin@luma.com').first()
        if not admin_user:
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin_user = Usuario(
                nombre='Administrador',
                correo='admin@luma.com',
                id_tipo=admin_tipo.id_tipo
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            if admin_password == 'admin123':
                print("ADVERTENCIA: El usuario admin usa la contraseña por defecto. "
                      "Establezca ADMIN_PASSWORD en producción.")
    
    print("Base de datos inicializada correctamente.")


with app.app_context():
    init_database()







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


# ==================== AUTENTICACIÓN ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if usuario and usuario.check_password(password):
            if not usuario.activo:
                flash('Su cuenta está desactivada. Contacte al administrador.', 'danger')
                return redirect(url_for('login'))
            
            login_user(usuario)
            flash(f'¡Bienvenido {usuario.nombre}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('inicio'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('inicio'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        telefono = request.form.get('telefono', '')
        
        # Validaciones
        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('registro'))
        
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('registro'))
        
        # Crear usuario como cliente
        tipo_cliente = TipoUsuario.query.filter_by(nombre='cliente').first()
        if not tipo_cliente:
            flash('Error en la configuración del sistema.', 'danger')
            return redirect(url_for('registro'))
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            id_tipo=tipo_cliente.id_tipo
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.flush()
        
        # Crear registro de cliente
        nuevo_cliente = Cliente(
            id_usuario=nuevo_usuario.id_usuario,
            telefono=telefono
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')




# ==================== PANEL DE ADMINISTRACIÓN ====================

@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    usuarios = Usuario.query.all()
    tipos = TipoUsuario.query.all()
    productos = Producto.query.all()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    insumos = Insumo.query.all()
    pedidos = Pedido.query.all()
    return render_template('admin/panel.html', 
                         usuarios=usuarios, 
                         tipos=tipos, 
                         productos=productos,
                         clientes=clientes,
                         empleados=empleados,
                         insumos=insumos,
                         pedidos=pedidos)


#CRUD PRODUCTOS
@app.route('/admin/productos')
@login_required
@admin_required
def lista_productos():
    productos = Producto.query.all()
    return render_template('admin/productos_lista.html', productos=productos)

@app.route('/admin/productos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form.get('precio', 0))
        stock = int(request.form.get('stock', 0))
        
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('lista_productos'))
    
    return render_template('admin/productos_form.html', producto=None)

@app.route('/admin/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        producto.nombre = request.form.get('nombre')
        producto.descripcion = request.form.get('descripcion', '')
        producto.precio = float(request.form.get('precio', 0))
        producto.stock = int(request.form.get('stock', 0))
        db.session.commit()
        
        flash('Producto actualizado.', 'success')
        return redirect(url_for('lista_productos'))
    
    return render_template('admin/productos_form.html', producto=producto)

@app.route('/admin/productos/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    
    flash('Producto eliminado.', 'success')
    return redirect(url_for('lista_productos'))



# CRUD TIPOS DE USUARIO
@app.route('/admin/tipos')
@login_required
@admin_required
def lista_tipos():
    tipos = TipoUsuario.query.all()
    return render_template('admin/tipos_lista.html', tipos=tipos)


@app.route('/admin/tipos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_tipo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        
        if TipoUsuario.query.filter_by(nombre=nombre).first():
            flash('Ya existe un tipo con ese nombre.', 'danger')
            return redirect(url_for('crear_tipo'))
        
        nuevo_tipo = TipoUsuario(nombre=nombre, descripcion=descripcion)
        db.session.add(nuevo_tipo)
        db.session.commit()
        
        flash('Tipo de usuario creado exitosamente.', 'success')
        return redirect(url_for('lista_tipos'))
    
    return render_template('admin/tipo_form.html', tipo=None)


@app.route('/admin/tipos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_tipo(id):
    tipo = TipoUsuario.query.get_or_404(id)
    
    if request.method == 'POST':
        tipo.nombre = request.form.get('nombre')
        tipo.descripcion = request.form.get('descripcion', '')
        db.session.commit()
        
        flash('Tipo de usuario actualizado.', 'success')
        return redirect(url_for('lista_tipos'))
    
    return render_template('admin/tipo_form.html', tipo=tipo)


@app.route('/admin/tipos/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_tipo(id):
    tipo = TipoUsuario.query.get_or_404(id)
    
    # Verificar que no haya usuarios con este tipo
    if tipo.usuarios:
        flash('No se puede eliminar: hay usuarios con este tipo.', 'danger')
        return redirect(url_for('lista_tipos'))
    
    db.session.delete(tipo)
    db.session.commit()
    
    flash('Tipo de usuario eliminado.', 'success')
    return redirect(url_for('lista_tipos'))


# CRUD USUARIOS
@app.route('/admin/usuarios')
@login_required
@admin_required
def lista_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios_lista.html', usuarios=usuarios)


@app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    tipos = TipoUsuario.query.all()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        id_tipo = request.form.get('id_tipo')
        
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('crear_usuario'))
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            id_tipo=int(id_tipo)
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('lista_usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=None, tipos=tipos)


@app.route('/admin/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    tipos = TipoUsuario.query.all()
    
    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre')
        usuario.correo = request.form.get('correo')
        usuario.id_tipo = int(request.form.get('id_tipo'))
        usuario.activo = 'activo' in request.form
        
        # Actualizar contraseña solo si se proporcionó una nueva
        new_password = request.form.get('password')
        if new_password:
            usuario.set_password(new_password)
        
        db.session.commit()
        
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('lista_usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=usuario, tipos=tipos)


@app.route('/admin/usuarios/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    # No permitir eliminar el propio usuario
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puede eliminar su propio usuario.', 'danger')
        return redirect(url_for('lista_usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('lista_usuarios'))


# CRUD CLIENTES
@app.route('/admin/clientes')
@login_required
@admin_required
def lista_clientes():
    clientes = Cliente.query.all()
    return render_template('admin/clientes_lista.html', clientes=clientes)


@app.route('/admin/clientes/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_cliente():
    usuarios = Usuario.query.all()
    
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        telefono = request.form.get('telefono', '')
        
        # Validar que id_usuario no esté vacío
        if not id_usuario:
            flash('Debe seleccionar un usuario.', 'danger')
            return redirect(url_for('crear_cliente'))
        
        try:
            id_usuario_int = int(id_usuario)
        except (ValueError, TypeError):
            flash('Usuario inválido.', 'danger')
            return redirect(url_for('crear_cliente'))
        
        # Verificar que el usuario no tenga ya un registro de cliente
        if Cliente.query.filter_by(id_usuario=id_usuario_int).first():
            flash('Este usuario ya tiene un registro de cliente.', 'danger')
            return redirect(url_for('crear_cliente'))
        
        nuevo_cliente = Cliente(
            id_usuario=id_usuario_int,
            telefono=telefono
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        flash('Cliente creado exitosamente.', 'success')
        return redirect(url_for('lista_clientes'))
    
    return render_template('admin/cliente_form.html', cliente=None, usuarios=usuarios)


@app.route('/admin/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    usuarios = Usuario.query.all()
    
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        
        if not id_usuario:
            flash('Debe seleccionar un usuario.', 'danger')
            return redirect(url_for('editar_cliente', id=id))
        
        try:
            cliente.id_usuario = int(id_usuario)
        except (ValueError, TypeError):
            flash('Usuario inválido.', 'danger')
            return redirect(url_for('editar_cliente', id=id))
        
        cliente.telefono = request.form.get('telefono', '')
        db.session.commit()
        
        flash('Cliente actualizado.', 'success')
        return redirect(url_for('lista_clientes'))
    
    return render_template('admin/cliente_form.html', cliente=cliente, usuarios=usuarios)


@app.route('/admin/clientes/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar que no haya pedidos asociados
    if cliente.pedidos:
        flash('No se puede eliminar: el cliente tiene pedidos asociados.', 'danger')
        return redirect(url_for('lista_clientes'))
    
    db.session.delete(cliente)
    db.session.commit()
    
    flash('Cliente eliminado.', 'success')
    return redirect(url_for('lista_clientes'))


# CRUD EMPLEADOS
@app.route('/admin/empleados')
@login_required
@admin_required
def lista_empleados():
    empleados = Empleado.query.all()
    return render_template('admin/empleados_lista.html', empleados=empleados)


@app.route('/admin/empleados/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_empleado():
    usuarios = Usuario.query.all()
    
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        puesto = request.form.get('puesto', '')
        
        # Validar que id_usuario no esté vacío
        if not id_usuario:
            flash('Debe seleccionar un usuario.', 'danger')
            return redirect(url_for('crear_empleado'))
        
        try:
            id_usuario_int = int(id_usuario)
        except (ValueError, TypeError):
            flash('Usuario inválido.', 'danger')
            return redirect(url_for('crear_empleado'))
        
        # Verificar que el usuario no tenga ya un registro de empleado
        if Empleado.query.filter_by(id_usuario=id_usuario_int).first():
            flash('Este usuario ya tiene un registro de empleado.', 'danger')
            return redirect(url_for('crear_empleado'))
        
        nuevo_empleado = Empleado(
            id_usuario=id_usuario_int,
            puesto=puesto
        )
        db.session.add(nuevo_empleado)
        db.session.commit()
        
        flash('Empleado creado exitosamente.', 'success')
        return redirect(url_for('lista_empleados'))
    
    return render_template('admin/empleado_form.html', empleado=None, usuarios=usuarios)


@app.route('/admin/empleados/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    usuarios = Usuario.query.all()
    
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        
        if not id_usuario:
            flash('Debe seleccionar un usuario.', 'danger')
            return redirect(url_for('editar_empleado', id=id))
        
        try:
            empleado.id_usuario = int(id_usuario)
        except (ValueError, TypeError):
            flash('Usuario inválido.', 'danger')
            return redirect(url_for('editar_empleado', id=id))
        
        empleado.puesto = request.form.get('puesto', '')
        db.session.commit()
        
        flash('Empleado actualizado.', 'success')
        return redirect(url_for('lista_empleados'))
    
    return render_template('admin/empleado_form.html', empleado=empleado, usuarios=usuarios)


@app.route('/admin/empleados/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    
    # Verificar que no haya seguimientos asociados
    if empleado.seguimientos:
        flash('No se puede eliminar: el empleado tiene seguimientos de pedidos asociados.', 'danger')
        return redirect(url_for('lista_empleados'))
    
    db.session.delete(empleado)
    db.session.commit()
    
    flash('Empleado eliminado.', 'success')
    return redirect(url_for('lista_empleados'))


# CRUD INSUMOS
@app.route('/admin/insumos')
@login_required
@admin_required
def lista_insumos():
    insumos = Insumo.query.all()
    return render_template('admin/insumos_lista.html', insumos=insumos)


@app.route('/admin/insumos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_insumo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        cantidad_str = request.form.get('cantidad', '0')
        unidad = request.form.get('unidad', '')
        
        try:
            cantidad = int(cantidad_str)
        except (ValueError, TypeError):
            flash('Cantidad inválida. Debe ser un número entero.', 'danger')
            return redirect(url_for('crear_insumo'))
        
        nuevo_insumo = Insumo(
            nombre=nombre,
            descripcion=descripcion,
            cantidad=cantidad,
            unidad=unidad
        )
        db.session.add(nuevo_insumo)
        db.session.commit()
        
        flash('Insumo creado exitosamente.', 'success')
        return redirect(url_for('lista_insumos'))
    
    return render_template('admin/insumo_form.html', insumo=None)


@app.route('/admin/insumos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_insumo(id):
    insumo = Insumo.query.get_or_404(id)
    
    if request.method == 'POST':
        cantidad_str = request.form.get('cantidad', '0')
        
        try:
            cantidad = int(cantidad_str)
        except (ValueError, TypeError):
            flash('Cantidad inválida. Debe ser un número entero.', 'danger')
            return redirect(url_for('editar_insumo', id=id))
        
        insumo.nombre = request.form.get('nombre')
        insumo.descripcion = request.form.get('descripcion', '')
        insumo.cantidad = cantidad
        insumo.unidad = request.form.get('unidad', '')
        db.session.commit()
        
        flash('Insumo actualizado.', 'success')
        return redirect(url_for('lista_insumos'))
    
    return render_template('admin/insumo_form.html', insumo=insumo)


@app.route('/admin/insumos/eliminar/<int:id>')
@login_required
@admin_required
def eliminar_insumo(id):
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    
    flash('Insumo eliminado.', 'success')
    return redirect(url_for('lista_insumos'))


# ==================== PEDIDOS ====================

@app.route('/pedidos')
def pedidos():
    productos = Producto.query.all()
    return render_template('pedidos.html', productos=productos)


@app.route('/realizar_pedido', methods=['GET', 'POST'])
@login_required
def realizar_pedido():
    productos = Producto.query.all()
    
    if request.method == 'POST':
        # Obtener o crear cliente asociado al usuario
        cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
        
        if not cliente:
            # Crear registro de cliente si no existe
            cliente = Cliente(
                id_usuario=current_user.id_usuario,
                telefono=request.form.get('telefono', '')
            )
            db.session.add(cliente)
            db.session.flush()
        
        # Crear pedido
        nuevo_pedido = Pedido(
            id_cliente=cliente.id_cliente,
            fecha=datetime.utcnow(),
            estado='pendiente'
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # Agregar detalles del pedido
        productos_seleccionados = request.form.getlist('productos')
        cantidades = request.form.getlist('cantidades')
        
        for i, prod_id in enumerate(productos_seleccionados):
            if prod_id and cantidades[i]:
                detalle = DetallePedido(
                    id_pedido=nuevo_pedido.id_pedido,
                    id_producto=int(prod_id),
                    cantidad=int(cantidades[i])
                )
                db.session.add(detalle)
        
        # Crear seguimiento inicial
        seguimiento = SeguimientoPedido(
            id_pedido=nuevo_pedido.id_pedido,
            fecha=datetime.utcnow(),
            estado='pendiente',
            comentario='Pedido recibido'
        )
        db.session.add(seguimiento)
        db.session.commit()
        
        flash(f'Pedido #{nuevo_pedido.id_pedido} creado exitosamente.', 'success')
        return redirect(url_for('mis_pedidos'))
    
    return render_template('realizar_pedido.html', productos=productos)


@app.route('/mis_pedidos')
@login_required
def mis_pedidos():
    cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
    pedidos = []
    
    if cliente:
        pedidos = Pedido.query.filter_by(id_cliente=cliente.id_cliente).order_by(Pedido.fecha.desc()).all()
    
    return render_template('mis_pedidos.html', pedidos=pedidos)


@app.route('/rastrear_pedido', methods=['GET', 'POST'])
def rastrear_pedido():
    pedido = None
    seguimientos = []
    
    if request.method == 'POST' or request.args.get('id'):
        pedido_id = request.form.get('pedido_id') or request.args.get('id')
        
        if pedido_id:
            pedido = Pedido.query.get(pedido_id)
            
            if pedido:
                # Verificar autorización: el pedido puede ser visto por:
                # 1. El cliente dueño del pedido
                # 2. Un admin o empleado autenticado
                # 3. Cualquiera puede ver información básica del estado (sin datos sensibles)
                can_view_details = False
                
                if current_user.is_authenticated:
                    if current_user.is_admin or current_user.is_empleado:
                        can_view_details = True
                    else:
                        cliente = Cliente.query.filter_by(id_usuario=current_user.id_usuario).first()
                        if cliente and pedido.id_cliente == cliente.id_cliente:
                            can_view_details = True
                
                if can_view_details:
                    seguimientos = SeguimientoPedido.query.filter_by(
                        id_pedido=pedido.id_pedido
                    ).order_by(SeguimientoPedido.fecha.desc()).all()
                else:
                    # Solo mostrar información básica del estado sin detalles sensibles
                    seguimientos = []
                    flash('Para ver los detalles completos del pedido, inicie sesión como el cliente propietario.', 'info')
            else:
                flash('Pedido no encontrado.', 'warning')
    
    return render_template('rastrear_pedido.html', pedido=pedido, seguimientos=seguimientos)


# ==================== GESTIÓN DE PEDIDOS (ADMIN/EMPLEADO) ====================

@app.route('/admin/pedidos')
@login_required
def admin_pedidos():
    if not (current_user.is_admin or current_user.is_empleado):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('admin/pedidos_lista.html', pedidos=pedidos)


@app.route('/admin/pedidos/<int:id>/actualizar', methods=['GET', 'POST'])
@login_required
def actualizar_pedido(id):
    if not (current_user.is_admin or current_user.is_empleado):
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('inicio'))
    
    pedido = Pedido.query.get_or_404(id)
    
    if request.method == 'POST':
        nuevo_estado = request.form.get('estado')
        comentario = request.form.get('comentario', '')
        
        pedido.estado = nuevo_estado
        
        # Obtener empleado actual
        empleado = Empleado.query.filter_by(id_usuario=current_user.id_usuario).first()
        
        # Crear seguimiento
        seguimiento = SeguimientoPedido(
            id_pedido=pedido.id_pedido,
            fecha=datetime.utcnow(),
            estado=nuevo_estado,
            id_empleado=empleado.id_empleado if empleado else None,
            comentario=comentario
        )
        db.session.add(seguimiento)
        db.session.commit()
        
        flash('Estado del pedido actualizado.', 'success')
        return redirect(url_for('admin_pedidos'))
    
    estados = ['pendiente', 'en_proceso', 'en_produccion', 'listo', 'enviado', 'entregado', 'cancelado']
    return render_template('admin/pedido_actualizar.html', pedido=pedido, estados=estados)


# ==================== PANEL DE EMPLEADO ====================

@app.route('/empleado_panel')
@login_required
@empleado_required
def empleado_panel():
    productos = Producto.query.all()
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).limit(10).all()
    return render_template('empleado/panel.html', productos=productos, pedidos=pedidos)


# Empleado - Productos (CRUD completo)
@app.route('/empleado/productos')
@login_required
@empleado_required
def empleado_lista_productos():
    productos = Producto.query.all()
    return render_template('empleado/productos_lista.html', productos=productos)


@app.route('/empleado/productos/crear', methods=['GET', 'POST'])
@login_required
@empleado_required
def empleado_crear_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion', '')
        precio_str = request.form.get('precio', '0')
        stock_str = request.form.get('stock', '0')
        
        try:
            precio = float(precio_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash('Precio o stock inválido. Verifique los valores ingresados.', 'danger')
            return redirect(url_for('empleado_crear_producto'))
        
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        
        flash('Producto creado exitosamente.', 'success')
        return redirect(url_for('empleado_lista_productos'))
    
    return render_template('empleado/producto_form.html', producto=None)


@app.route('/empleado/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empleado_required
def empleado_editar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    if request.method == 'POST':
        precio_str = request.form.get('precio', '0')
        stock_str = request.form.get('stock', '0')
        
        try:
            precio = float(precio_str)
            stock = int(stock_str)
        except (ValueError, TypeError):
            flash('Precio o stock inválido. Verifique los valores ingresados.', 'danger')
            return redirect(url_for('empleado_editar_producto', id=id))
        
        producto.nombre = request.form.get('nombre')
        producto.descripcion = request.form.get('descripcion', '')
        producto.precio = precio
        producto.stock = stock
        db.session.commit()
        
        flash('Producto actualizado.', 'success')
        return redirect(url_for('empleado_lista_productos'))
    
    return render_template('empleado/producto_form.html', producto=producto)


@app.route('/empleado/productos/eliminar/<int:id>')
@login_required
@empleado_required
def empleado_eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    
    flash('Producto eliminado.', 'success')
    return redirect(url_for('empleado_lista_productos'))


# Empleado - Pedidos (CRUD completo)
@app.route('/empleado/pedidos')
@login_required
@empleado_required
def empleado_lista_pedidos():
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('empleado/pedidos_lista.html', pedidos=pedidos)


@app.route('/empleado/pedidos/crear', methods=['GET', 'POST'])
@login_required
@empleado_required
def empleado_crear_pedido():
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        fecha = datetime.utcnow()
        estado = request.form.get('estado', 'pendiente')
        
        # Validar id_cliente
        if not id_cliente:
            flash('Debe seleccionar un cliente.', 'danger')
            return redirect(url_for('empleado_crear_pedido'))
        
        try:
            id_cliente_int = int(id_cliente)
        except (ValueError, TypeError):
            flash('Cliente inválido.', 'danger')
            return redirect(url_for('empleado_crear_pedido'))
        
        nuevo_pedido = Pedido(
            id_cliente=id_cliente_int,
            fecha=fecha,
            estado=estado
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # Agregar detalles del pedido si se proporcionaron
        productos_seleccionados = request.form.getlist('productos[]')
        cantidades = request.form.getlist('cantidades[]')
        
        for i, prod_id in enumerate(productos_seleccionados):
            if prod_id and i < len(cantidades) and cantidades[i]:
                try:
                    detalle = DetallePedido(
                        id_pedido=nuevo_pedido.id_pedido,
                        id_producto=int(prod_id),
                        cantidad=int(cantidades[i])
                    )
                    db.session.add(detalle)
                except (ValueError, TypeError):
                    # Skip invalid entries
                    continue
        
        # Crear seguimiento inicial
        empleado = Empleado.query.filter_by(id_usuario=current_user.id_usuario).first()
        seguimiento = SeguimientoPedido(
            id_pedido=nuevo_pedido.id_pedido,
            fecha=datetime.utcnow(),
            estado=estado,
            id_empleado=empleado.id_empleado if empleado else None,
            comentario='Pedido creado por empleado'
        )
        db.session.add(seguimiento)
        db.session.commit()
        
        flash('Pedido creado exitosamente.', 'success')
        return redirect(url_for('empleado_lista_pedidos'))
    
    return render_template('empleado/pedido_form.html', pedido=None, clientes=clientes, productos=productos)


@app.route('/empleado/pedidos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@empleado_required
def empleado_editar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        
        # Validar id_cliente
        if not id_cliente:
            flash('Debe seleccionar un cliente.', 'danger')
            return redirect(url_for('empleado_editar_pedido', id=id))
        
        try:
            pedido.id_cliente = int(id_cliente)
        except (ValueError, TypeError):
            flash('Cliente inválido.', 'danger')
            return redirect(url_for('empleado_editar_pedido', id=id))
        
        pedido.estado = request.form.get('estado')
        
        # Actualizar detalles si se proporcionaron
        # Eliminar detalles existentes
        DetallePedido.query.filter_by(id_pedido=pedido.id_pedido).delete()
        
        # Agregar nuevos detalles
        productos_seleccionados = request.form.getlist('productos[]')
        cantidades = request.form.getlist('cantidades[]')
        
        for i, prod_id in enumerate(productos_seleccionados):
            if prod_id and i < len(cantidades) and cantidades[i]:
                try:
                    detalle = DetallePedido(
                        id_pedido=pedido.id_pedido,
                        id_producto=int(prod_id),
                        cantidad=int(cantidades[i])
                    )
                    db.session.add(detalle)
                except (ValueError, TypeError):
                    # Skip invalid entries
                    continue
        
        # Crear seguimiento de la actualización
        empleado = Empleado.query.filter_by(id_usuario=current_user.id_usuario).first()
        seguimiento = SeguimientoPedido(
            id_pedido=pedido.id_pedido,
            fecha=datetime.utcnow(),
            estado=pedido.estado,
            id_empleado=empleado.id_empleado if empleado else None,
            comentario='Pedido actualizado por empleado'
        )
        db.session.add(seguimiento)
        db.session.commit()
        
        flash('Pedido actualizado.', 'success')
        return redirect(url_for('empleado_lista_pedidos'))
    
    return render_template('empleado/pedido_form.html', pedido=pedido, clientes=clientes, productos=productos)


@app.route('/empleado/pedidos/eliminar/<int:id>')
@login_required
@empleado_required
def empleado_eliminar_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    
    # Eliminar detalles asociados
    DetallePedido.query.filter_by(id_pedido=pedido.id_pedido).delete()
    
    # Eliminar seguimientos asociados
    SeguimientoPedido.query.filter_by(id_pedido=pedido.id_pedido).delete()
    
    db.session.delete(pedido)
    db.session.commit()
    
    flash('Pedido eliminado.', 'success')
    return redirect(url_for('empleado_lista_pedidos'))


@app.route('/empleado/pedidos/<int:id>/actualizar', methods=['GET', 'POST'])
@login_required
@empleado_required
def empleado_actualizar_estado_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    
    if request.method == 'POST':
        nuevo_estado = request.form.get('estado')
        comentario = request.form.get('comentario', '')
        
        pedido.estado = nuevo_estado
        
        # Obtener empleado actual
        empleado = Empleado.query.filter_by(id_usuario=current_user.id_usuario).first()
        
        # Crear seguimiento
        seguimiento = SeguimientoPedido(
            id_pedido=pedido.id_pedido,
            fecha=datetime.utcnow(),
            estado=nuevo_estado,
            id_empleado=empleado.id_empleado if empleado else None,
            comentario=comentario
        )
        db.session.add(seguimiento)
        db.session.commit()
        
        flash('Estado del pedido actualizado.', 'success')
        return redirect(url_for('empleado_lista_pedidos'))
    
    estados = ['pendiente', 'en_proceso', 'en_produccion', 'listo', 'enviado', 'entregado', 'cancelado']
    return render_template('empleado/pedido_actualizar.html', pedido=pedido, estados=estados)


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)