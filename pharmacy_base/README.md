# Pharmacy Base

## Descripción

Módulo base para el sistema de gestión de farmacias. Proporciona los modelos fundamentales para productos farmacéuticos, pacientes, médicos y seguros.

## Características

- **Categorías Farmacéuticas**: Clasificación especializada de productos con tipos como medicamentos con receta, venta libre, controlados, etc.
- **Gestión de Productos**: Extensión de productos con información farmacéutica detallada (principio activo, concentración, forma farmacéutica, etc.)
- **Pacientes**: Registro completo con información médica, alergias, condiciones crónicas y medicamentos actuales
- **Médicos Prescriptores**: Gestión de médicos con especialidades y licencias
- **Seguros Médicos**: Sistema completo de administración de seguros con cálculo automático de copagos y deducibles
- **Laboratorios**: Registro de laboratorios farmacéuticos

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar lista de aplicaciones en Odoo
3. Buscar "Pharmacy Base" en aplicaciones
4. Hacer clic en Instalar

## Configuración

### Categorías Farmacéuticas

Ir a: Farmacia > Configuración > Categorías Farmacéuticas

Las categorías se clasifican automáticamente según el tipo:
- **Prescription**: Requieren receta médica obligatoria
- **OTC**: Venta libre sin receta
- **Controlled**: Medicamentos controlados con registro especial

### Pacientes

Ir a: Farmacia > Maestros > Pacientes

Los pacientes reciben un código único generado automáticamente (Ej: PAC000123).

### Productos Farmacéuticos

Ir a: Farmacia > Maestros > Productos Farmacéuticos

Para crear un producto farmacéutico:
1. Marcar la casilla "Es Producto Farmacéutico"
2. Llenar los campos obligatorios (principio activo, forma farmacéutica)
3. Seleccionar categoría farmacéutica apropiada
4. Agregar información clínica opcional

### Seguros Médicos

Ir a: Farmacia > Maestros > Seguros Médicos

Registro de pólizas de seguros con:
- Información de póliza y miembro
- Configuración de copagos y coseguros
- Control de deducibles anuales
- Cálculo automático de costos para pacientes

## Uso

### Registrar un nuevo paciente

1. Ir a Farmacia > Maestros > Pacientes
2. Hacer clic en "Crear"
3. Ingresar datos básicos (nombre, cédula, etc.)
4. Marcar "Es Paciente"
5. Agregar información médica:
   - Alergias conocidas
   - Condiciones crónicas
   - Medicamentos actuales
6. Guardar

### Agregar seguro a un paciente

1. Abrir ficha del paciente
2. Ir a pestaña "Información del Paciente"
3. Hacer clic en "Agregar" en la sección "Seguros Médicos"
4. Completar datos de la póliza
5. Configurar costos (copago, coseguro, deducible)
6. Guardar

### Crear producto farmacéutico

1. Ir a Farmacia > Maestros > Productos Farmacéuticos
2. Hacer clic en "Crear"
3. Marcar "Es Producto Farmacéutico"
4. Completar información farmacéutica:
   - Principio activo (obligatorio)
   - Forma farmacéutica y concentración
   - Presentación
   - Laboratorio fabricante
   - Información clínica (opcional)
5. Guardar

## Cálculo de Costos de Seguros

El sistema calcula automáticamente el costo que debe pagar el paciente:

1. **Verifica validez de la cobertura**
2. **Aplica deducible** (si está pendiente)
3. **Aplica copago fijo** o **coseguro porcentual**
4. **Retorna**: monto del paciente, monto del seguro, razón del cálculo

## Dependencias

- **base**: Módulo base de Odoo
- **product**: Gestión de productos
- **stock**: Gestión de inventario

## Seguridad

El módulo incluye tres niveles de acceso:

- **Usuario**: Acceso básico de lectura y creación
- **Farmacéutico**: Gestión completa de operaciones
- **Gerente**: Acceso administrativo completo

## Tests

El módulo incluye tests completos para validar:
- Creación y validación de productos farmacéuticos
- Generación automática de códigos de paciente
- Cálculos de seguros y copagos
- Validaciones de fechas y restricciones

Para ejecutar los tests:

```bash
./odoo-bin -c odoo.conf -d test_db -i pharmacy_base --test-enable --stop-after-init
```

## Soporte

Para soporte técnico o reportar issues, contacte al equipo de desarrollo o abra un issue en el repositorio del proyecto.

## Licencia

LGPL-3 - Ver archivo LICENSE para detalles.

## Autor

Vertical Pharmacy Team - Desarrollo de soluciones farmacéuticas para Odoo