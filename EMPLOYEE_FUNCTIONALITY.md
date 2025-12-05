# Funcionalidad de Usuario Empleado

## Descripción

Este documento describe la funcionalidad implementada para el tipo de usuario "empleado" en el sistema Luma.

## Requisitos Funcionales Implementados

### 1. Visualización de Pedidos Pendientes y En Proceso

El sistema permite a los empleados visualizar:
- **Pedidos Pendientes**: Pedidos que aún no han sido iniciados y requieren atención inmediata
- **Pedidos En Proceso**: Pedidos que están siendo trabajados actualmente

#### Características:
- Dashboard dedicado con estadísticas en tiempo real
- Vista separada para pedidos pendientes y en proceso
- Información detallada de cada pedido:
  - Número de pedido
  - Cliente (nombre, correo, teléfono)
  - Fecha del pedido
  - Estado actual
  - Productos solicitados con cantidades
  - Último comentario (para pedidos en proceso)

### 2. Registro de Avances y Cambios de Estado

El sistema permite a los empleados:
- **Actualizar el estado de los pedidos** a través de la interfaz de gestión
- **Registrar comentarios** sobre los avances y cambios realizados
- **Mantener un historial completo** de todos los cambios de estado

#### Estados disponibles:
- `pendiente` - Pedido recibido, esperando procesamiento
- `en_proceso` - Pedido en producción
- `en_produccion` - Pedido siendo elaborado
- `listo` - Pedido terminado, listo para entrega
- `enviado` - Pedido enviado al cliente
- `entregado` - Pedido entregado exitosamente
- `cancelado` - Pedido cancelado

#### Seguimiento (Tracking):
- Cada cambio de estado genera un registro en `SeguimientoPedido`
- Se registra la fecha y hora del cambio
- Se asocia el empleado que realizó el cambio
- Se permite agregar comentarios descriptivos

## Rutas Implementadas

### `/empleado/dashboard`
**Método**: GET  
**Autenticación**: Requerida (solo empleados)  
**Descripción**: Dashboard principal del empleado que muestra:
- Estadísticas de pedidos pendientes y en proceso
- Lista detallada de todos los pedidos pendientes
- Lista detallada de todos los pedidos en proceso
- Botones de acción para gestionar y ver detalles

### `/admin/pedidos/<int:id>/actualizar`
**Método**: GET, POST  
**Autenticación**: Requerida (empleados y administradores)  
**Descripción**: Permite actualizar el estado de un pedido específico
- Muestra información completa del pedido
- Formulario para cambiar el estado
- Campo para agregar comentarios
- Historial de seguimiento del pedido

**Modificación**: Ahora redirige al dashboard de empleado después de actualizar (si el usuario es empleado)

## Navegación

El sistema actualiza automáticamente la navegación según el tipo de usuario:

- **Empleados**: Ven el enlace "Panel Empleado" en lugar de "Admin"
- **Administradores**: Ven el enlace "Admin" con acceso completo
- **Empleados no tienen acceso** a "Mis Pedidos" (funcionalidad de cliente)

## Acceso y Permisos

### Empleados pueden:
✅ Acceder al dashboard de empleado  
✅ Ver todos los pedidos pendientes y en proceso  
✅ Actualizar el estado de cualquier pedido  
✅ Agregar comentarios sobre el progreso  
✅ Ver el historial completo de seguimiento  

### Empleados NO pueden:
❌ Acceder al panel de administración completo  
❌ Gestionar usuarios o tipos de usuario  
❌ Crear nuevos pedidos (funcionalidad de cliente)  

## Uso del Sistema

### Para Crear un Usuario Empleado:

1. Un administrador debe crear el usuario con tipo "empleado"
2. Crear el registro asociado en la tabla `empleados`:
   ```sql
   INSERT INTO empleados (id_usuario, puesto) VALUES (?, ?);
   ```

### Para Usar el Sistema como Empleado:

1. Iniciar sesión con credenciales de empleado
2. Click en "Panel Empleado" en el menú de navegación
3. Revisar los pedidos pendientes y en proceso
4. Click en "Gestionar" para actualizar el estado de un pedido
5. Seleccionar el nuevo estado y agregar un comentario descriptivo
6. Guardar los cambios

## Base de Datos

### Modelos Utilizados:

- **Usuario**: Usuario del sistema con tipo "empleado"
- **TipoUsuario**: Define el tipo "empleado"
- **Empleado**: Información adicional del empleado (puesto)
- **Pedido**: Pedidos del sistema
- **DetallePedido**: Productos incluidos en cada pedido
- **SeguimientoPedido**: Historial de cambios de estado

### Consultas Principales:

```python
# Obtener pedidos pendientes
pedidos_pendientes = Pedido.query.filter_by(estado='pendiente').order_by(Pedido.fecha.asc()).all()

# Obtener pedidos en proceso
pedidos_en_proceso = Pedido.query.filter_by(estado='en_proceso').order_by(Pedido.fecha.asc()).all()

# Registrar cambio de estado
seguimiento = SeguimientoPedido(
    id_pedido=pedido.id_pedido,
    fecha=datetime.utcnow(),
    estado=nuevo_estado,
    id_empleado=empleado.id_empleado,
    comentario=comentario
)
```

## Interfaz de Usuario

### Dashboard de Empleado:
- Diseño responsivo con Bootstrap 5
- Tarjetas de estadísticas con gradientes visuales
- Iconos de Font Awesome para mejor UX
- Badges de colores para estados de pedidos
- Hover effects en las tarjetas de pedidos
- Botones de acción claramente identificados

### Paleta de Colores por Estado:
- **Pendiente**: Amarillo (#ffc107)
- **En Proceso**: Cian (#17a2b8)
- **En Producción**: Púrpura (#6f42c1)
- **Listo**: Verde (#28a745)
- **Enviado**: Azul (#007bff)
- **Entregado**: Verde agua (#20c997)
- **Cancelado**: Rojo (#dc3545)

## Seguridad

- Autenticación requerida mediante Flask-Login
- Verificación de tipo de usuario en cada ruta
- Redirección automática si no tiene permisos
- Mensajes flash informativos para el usuario
- Asociación de cambios con el empleado que los realizó

## Mejoras Futuras (Sugerencias)

- Filtros adicionales por fecha, cliente o estado
- Búsqueda de pedidos por número
- Notificaciones en tiempo real
- Exportación de reportes
- Asignación de pedidos a empleados específicos
- Vista de calendario con pedidos programados
