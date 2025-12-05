# Guía Rápida de Inicio - Panel de Empleado

## 🚀 Inicio Rápido

### Crear un Usuario Empleado

**Opción 1: Mediante la interfaz de administración**
1. Iniciar sesión como administrador (admin@luma.com)
2. Ir a "Admin" → "Gestión de Usuarios"
3. Click en "Crear Usuario"
4. Completar los datos:
   - Nombre: [Nombre del empleado]
   - Correo: [correo@ejemplo.com]
   - Contraseña: [contraseña segura]
   - Tipo de Usuario: **empleado**
5. Guardar

**Opción 2: Mediante consola/base de datos**
```sql
-- 1. Crear el usuario
INSERT INTO usuarios (nombre, correo, contrasena_hash, id_tipo, activo)
VALUES ('Juan Empleado', 'juan@luma.com', 'hash_password', 2, TRUE);

-- 2. Crear el registro de empleado
INSERT INTO empleados (id_usuario, puesto)
VALUES (LAST_INSERT_ID(), 'Operador de Impresión');
```

### Usar el Panel de Empleado

#### 1️⃣ Iniciar Sesión
- Ir a la página de login
- Ingresar credenciales del empleado
- Click en "Iniciar Sesión"

#### 2️⃣ Acceder al Dashboard
- En el menú superior, click en **"Panel Empleado"**
- Verás el dashboard con dos secciones principales:
  - 📋 Pedidos Pendientes
  - ⚙️ Pedidos En Proceso

#### 3️⃣ Ver Información de Pedidos
Cada pedido muestra:
- 🔢 **Número de pedido**
- 👤 **Cliente**: Nombre, correo y teléfono
- 📅 **Fecha**: Cuándo se realizó el pedido
- 🏷️ **Estado**: Badge de color según el estado
- 📦 **Productos**: Lista con cantidades
- 💬 **Último comentario**: (Solo en pedidos en proceso)

#### 4️⃣ Gestionar un Pedido

**Paso a paso:**
1. En el pedido que quieres actualizar, click en **"Gestionar"**
2. Verás la página de actualización con:
   - Información completa del pedido
   - Formulario para cambiar el estado
   - Campo para agregar comentarios
   - Historial de cambios anteriores

3. Seleccionar el **nuevo estado**:
   - `pendiente` → Recién recibido
   - `en_proceso` → Comenzando a trabajar
   - `en_produccion` → En producción activa
   - `listo` → Terminado, listo para entrega
   - `enviado` → Enviado al cliente
   - `entregado` → Entregado exitosamente
   - `cancelado` → Cancelado

4. Agregar un **comentario** (opcional pero recomendado):
   - Ejemplo: "Comenzando impresión de tarjetas"
   - Ejemplo: "Diseño aprobado por cliente, en producción"
   - Ejemplo: "Material listo para recoger"

5. Click en **"Actualizar Estado"**

6. El sistema:
   - ✅ Actualiza el estado del pedido
   - ✅ Guarda un registro en el historial
   - ✅ Asocia tu usuario al cambio
   - ✅ Te regresa al dashboard

#### 5️⃣ Ver Detalles Completos
- Click en **"Ver"** para ver el seguimiento completo del pedido
- Podrás ver todo el historial de cambios

## 📊 Dashboard - Características

### Tarjetas de Estadísticas
- **Amarillo/Rosa**: Pedidos Pendientes (requieren atención)
- **Azul/Púrpura**: Pedidos En Proceso (en progreso)
- Números grandes muestran la cantidad

### Tarjetas de Pedidos
- **Hover effect**: Se elevan al pasar el cursor
- **Badges de colores**: Identifican el estado rápidamente
- **Información organizada**: Fácil de leer y entender
- **Acciones rápidas**: Botones siempre visibles

## 🎨 Códigos de Color por Estado

| Estado | Color | Significado |
|--------|-------|-------------|
| Pendiente | 🟡 Amarillo | Requiere atención |
| En Proceso | 🔵 Cian | Trabajando en ello |
| En Producción | 🟣 Púrpura | Producción activa |
| Listo | 🟢 Verde | Completado |
| Enviado | 🔵 Azul | En tránsito |
| Entregado | 🟢 Verde Agua | Finalizado |
| Cancelado | 🔴 Rojo | Cancelado |

## 💡 Mejores Prácticas

### Para Empleados:
1. **Revisar el dashboard regularmente** para ver nuevos pedidos pendientes
2. **Actualizar estados inmediatamente** cuando cambien
3. **Agregar comentarios descriptivos** en cada actualización
4. **Comunicar problemas** si un pedido se demora
5. **Verificar información del cliente** antes de contactarlos

### Comentarios Útiles:
✅ Buenos ejemplos:
- "Comenzando preparación de archivos para impresión"
- "Material en proceso, estimado 2 horas"
- "Esperando aprobación del cliente para proceder"
- "Impresión completada, en proceso de corte y acabado"

❌ Evitar:
- "ok" (muy genérico)
- Sin comentario (pierde información valiosa)
- Comentarios confusos o poco descriptivos

## 🔒 Seguridad y Permisos

### Los empleados PUEDEN:
✅ Ver todos los pedidos pendientes y en proceso
✅ Actualizar el estado de cualquier pedido
✅ Agregar comentarios y notas
✅ Ver historial completo de seguimiento
✅ Ver información de contacto de clientes

### Los empleados NO PUEDEN:
❌ Acceder al panel de administración completo
❌ Crear o eliminar usuarios
❌ Modificar tipos de usuario
❌ Eliminar pedidos
❌ Ver pedidos como cliente (solo gestionarlos)

## 🆘 Solución de Problemas

### No veo el botón "Panel Empleado"
- Verificar que tu usuario tenga tipo "empleado"
- Cerrar sesión y volver a iniciar
- Contactar al administrador

### No puedo actualizar un pedido
- Verificar que estés autenticado
- Verificar tus permisos de empleado
- Refrescar la página
- Contactar al administrador si persiste

### No aparecen pedidos en el dashboard
- Es normal si no hay pedidos pendientes o en proceso
- Los pedidos completados/entregados no se muestran aquí
- Para ver todos los pedidos, un admin debe revisar el panel completo

## 📞 Soporte

Si tienes problemas o dudas:
1. Revisar esta guía
2. Consultar EMPLOYEE_FUNCTIONALITY.md (documentación técnica)
3. Contactar al administrador del sistema

---

**¡Listo! Ya puedes comenzar a gestionar pedidos como empleado.** 🎉
