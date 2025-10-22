# ESTÁNDARES DE DESARROLLO - MÓDULOS FARMACIA ODOO 18

## NOMENCLATURA

### Modelos Python

```python
# Nombres de modelos: snake_case con prefijo pharmacy
class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    _description = 'Receta Médica'
    _order = 'prescription_date desc'
```

### Campos

```python
# Campos: snake_case
patient_id = fields.Many2one('res.partner')
prescription_date = fields.Date()
total_amount = fields.Monetary()
```

### Métodos

```python
# Métodos públicos: snake_case
def action_validate(self):
    pass

# Métodos privados: _snake_case
def _compute_total_amount(self):
    pass

# Métodos CRUD: nombre estándar de Odoo
@api.model_create_multi
def create(self, vals_list):
    pass
```

### Archivos XML

```
# Vistas: modelo_vista_tipo.xml
pharmacy_prescription_views.xml
pharmacy_pos_templates.xml

# Datos: propósito.xml
sequences.xml
data.xml
demo.xml
```

### IDs de XML

```xml
<!-- Vistas: modelo_vista_tipo -->
<record id="pharmacy_prescription_form_view" model="ir.ui.view">
    ...
</record>

<!-- Acciones: action_modelo_descripción -->
<record id="action_pharmacy_prescriptions" model="ir.actions.act_window">
    ...
</record>

<!-- Menús: menu_contexto_descripción -->
<menuitem id="menu_pharmacy_prescriptions" .../>
```

### Sintaxis Odoo 18

En Odoo 18 se usan estas convenciones actualizadas:

```xml
<!-- Etiqueta list en lugar de tree -->
<list string="Registros">
    <field name="name"/>
    <field name="partner_id"/>
</list>

<!-- Atributos directos en lugar de attrs -->
<page string="Información" invisible="is_pharmaceutical == false">
    <field name="active_principle" required="1"/>
</page>

<!-- view_mode usa list en lugar de tree -->
<field name="view_mode">kanban,list,form</field>
```

---

## ESTRUCTURA DE CARPETAS

```
pharmacy_modulo/
├── __init__.py                 # Importa subcarpetas
├── __manifest__.py             # Declaración del módulo
│
├── models/                     # Modelos Python
│   ├── __init__.py
│   ├── modelo1.py
│   ├── modelo2.py
│   └── res_partner.py         # Extensiones a modelos existentes
│
├── views/                      # Vistas XML
│   ├── modelo1_views.xml
│   ├── modelo2_views.xml
│   └── menus.xml
│
├── security/                   # Seguridad
│   ├── ir.model.access.csv    # Permisos de modelo
│   └── security.xml            # Grupos y reglas de registro
│
├── data/                       # Datos de configuración
│   ├── sequences.xml
│   └── data.xml
│
├── demo/                       # Datos de demostración
│   └── demo.xml
│
├── wizards/                    # Wizards/Asistentes
│   ├── __init__.py
│   └── wizard_nombre.py
│
├── reports/                    # Reportes
│   ├── __init__.py
│   ├── report_templates.xml
│   └── report_nombre.py
│
├── static/                     # Recursos estáticos
│   ├── description/
│   │   ├── icon.png           # Icono 256x256
│   │   └── index.html         # Descripción del módulo
│   └── src/
│       ├── js/                # JavaScript
│       ├── xml/               # Templates OWL
│       └── scss/              # Estilos
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_modelo1.py
│   └── test_integration.py
│
└── README.md                   # Documentación
```

---

## ESTRUCTURA DE MODELOS

### Template Básico

```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class PharmacyModelo(models.Model):
    _name = 'pharmacy.modelo'
    _description = 'Descripción del Modelo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Si aplica
    _order = 'create_date desc'
    
    # 1. Campos básicos
    name = fields.Char(
        string='Nombre',
        required=True,
        index=True,
        tracking=True
    )
    
    active = fields.Boolean(
        default=True,
        tracking=True
    )
    
    # 2. Campos relacionales
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='restrict',
        index=True
    )
    
    # 3. Campos computados
    total_amount = fields.Monetary(
        string='Total',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )
    
    # 4. Campos de estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Hecho'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True)
    
    # 5. Constraints SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El nombre debe ser único.'),
    ]
    
    # 6. Métodos compute
    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('subtotal'))
    
    # 7. Validaciones (constrains)
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('La fecha final no puede ser anterior a la inicial.'))
    
    # 8. Métodos onchange
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.contact_name = self.partner_id.name
    
    # 9. Métodos CRUD
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pharmacy.modelo')
        return super().create(vals_list)
    
    def write(self, vals):
        # Lógica pre-write
        result = super().write(vals)
        # Lógica post-write
        return result
    
    def unlink(self):
        if any(record.state != 'draft' for record in self):
            raise UserError(_('Solo se pueden eliminar registros en borrador.'))
        return super().unlink()
    
    # 10. Métodos de acción
    def action_confirm(self):
        """Confirma el registro"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Solo se pueden confirmar borradores.'))
        self.state = 'confirmed'
    
    # 11. Métodos auxiliares privados
    def _prepare_invoice_values(self):
        """Prepara valores para crear factura"""
        self.ensure_one()
        return {
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
        }
```

---

## VISTAS XML

### Template de Vista Formulario

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="pharmacy_modelo_form_view" model="ir.ui.view">
        <field name="name">pharmacy.modelo.form</field>
        <field name="model">pharmacy.modelo</field>
        <field name="arch" type="xml">
            <form string="Título del Formulario">
                <!-- 1. Cabecera con botones de acción y estado -->
                <header>
                    <button name="action_confirm" 
                            string="Confirmar" 
                            type="object" 
                            class="oe_highlight"
                            invisible="state != 'draft'"/>
                    <button name="action_cancel" 
                            string="Cancelar" 
                            type="object"
                            invisible="state == 'cancelled'"/>
                    <field name="state" widget="statusbar" options="{'clickable': '1'}"/>
                </header>
                
                <sheet>
                    <!-- 2. Caja de botones (smart buttons) -->
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_invoices" 
                                type="object" 
                                class="oe_stat_button" 
                                icon="fa-file-text-o">
                            <field name="invoice_count" widget="statinfo" string="Facturas"/>
                        </button>
                    </div>
                    
                    <!-- 3. Widget de imagen/avatar si aplica -->
                    <field name="image" widget="image" class="oe_avatar"/>
                    
                    <!-- 4. Título del registro -->
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Nombre..."/>
                        </h1>
                    </div>
                    
                    <!-- 5. Grupos de campos -->
                    <group>
                        <group string="Información General">
                            <field name="partner_id" options="{'no_create': True}"/>
                            <field name="date"/>
                            <field name="reference"/>
                        </group>
                        <group string="Información Adicional">
                            <field name="user_id"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    
                    <!-- 6. Notebook con pestañas -->
                    <notebook>
                        <page string="Líneas" name="lines">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="product_id"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="subtotal"/>
                                </list>
                            </field>
                        </page>
                        <page string="Otra Información" name="other">
                            <group>
                                <field name="notes" nolabel="1"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
                
                <!-- 7. Chatter (si heredó mail.thread) -->
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
    
    <!-- Vista Tree -->
    <record id="pharmacy_modelo_list_view" model="ir.ui.view">
        <field name="name">pharmacy.modelo.list</field>
        <field name="model">pharmacy.modelo</field>
        <field name="arch" type="xml">
            <list string="Lista de Modelos"
                  decoration-info="state == 'draft'"
                  decoration-success="state == 'done'"
                  decoration-muted="state == 'cancelled'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="total_amount" widget="monetary"/>
                <field name="state" widget="badge" decoration-info="state == 'draft'"/>
            </list>
        </field>
    </record>
    
    <!-- Vista Kanban -->
    <record id="pharmacy_modelo_kanban_view" model="ir.ui.view">
        <field name="name">pharmacy.modelo.kanban</field>
        <field name="model">pharmacy.modelo</field>
        <field name="arch" type="xml">
            <kanban class="o_kanban_mobile">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="state"/>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_kanban_global_click">
                            <div class="o_kanban_record_top mb-0">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <field name="name"/>
                                    </strong>
                                </div>
                                <field name="state" widget="label_selection" 
                                       options="{'classes': {'draft': 'info', 'done': 'success'}}"/>
                            </div>
                            <div class="o_kanban_record_body">
                                <field name="partner_id"/>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>
    
    <!-- Filtros de búsqueda -->
    <record id="pharmacy_modelo_search_view" model="ir.ui.view">
        <field name="name">pharmacy.modelo.search</field>
        <field name="model">pharmacy.modelo</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="partner_id"/>
                <filter string="Borradores" name="draft" domain="[('state', '=', 'draft')]"/>
                <filter string="Confirmados" name="confirmed" domain="[('state', '=', 'confirmed')]"/>
                <separator/>
                <filter string="Fecha" name="date" date="date"/>
                <group expand="0" string="Agrupar Por">
                    <filter name="group_partner" string="Cliente" context="{'group_by': 'partner_id'}"/>
                    <filter name="group_state" string="Estado" context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>
    
    <!-- Acción de ventana -->
    <record id="action_pharmacy_modelos" model="ir.actions.act_window">
        <field name="name">Modelos</field>
        <field name="res_model">pharmacy.modelo</field>
        <field name="view_mode">kanban,list,form</field>
        <field name="context">{}</field>
        <field name="domain">[]</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Crear el primer registro
            </p>
            <p>
                Descripción de ayuda cuando no hay registros.
            </p>
        </field>
    </record>
</odoo>
```

---

## SEGURIDAD

### ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_pharmacy_modelo_user,pharmacy.modelo user,model_pharmacy_modelo,pharmacy_group_user,1,0,0,0
access_pharmacy_modelo_pharmacist,pharmacy.modelo pharmacist,model_pharmacy_modelo,pharmacy_group_pharmacist,1,1,1,0
access_pharmacy_modelo_manager,pharmacy.modelo manager,model_pharmacy_modelo,pharmacy_group_manager,1,1,1,1
```

### Reglas de Registro (security.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Regla: Solo ver propios registros -->
        <record id="pharmacy_modelo_rule_own" model="ir.rule">
            <field name="name">Ver solo propios registros</field>
            <field name="model_id" ref="model_pharmacy_modelo"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('pharmacy_group_user'))]"/>
        </record>
        
        <!-- Regla: Gerente ve todos -->
        <record id="pharmacy_modelo_rule_all" model="ir.rule">
            <field name="name">Gerente ve todos</field>
            <field name="model_id" ref="model_pharmacy_modelo"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('pharmacy_group_manager'))]"/>
        </record>
    </data>
</odoo>
```

---

## TESTING

### Estructura de Test

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError

@tagged('post_install', '-at_install')
class TestPharmacyModelo(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configuración que se ejecuta una vez
        cls.Modelo = cls.env['pharmacy.modelo']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner'
        })
    
    def setUp(self):
        super().setUp()
        # Configuración que se ejecuta antes de cada test
        self.record = self.Modelo.create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
    
    def test_create_record(self):
        """Test creación básica de registro"""
        self.assertTrue(self.record.id)
        self.assertEqual(self.record.name, 'Test Record')
        self.assertEqual(self.record.state, 'draft')
    
    def test_validation_error(self):
        """Test que validación lanza error"""
        with self.assertRaises(ValidationError):
            self.Modelo.create({
                'name': 'Test',
                'partner_id': self.partner.id,
                'end_date': '2024-01-01',
                'start_date': '2024-12-31',  # Error: fin antes de inicio
            })
    
    def test_action_confirm(self):
        """Test acción de confirmar"""
        self.record.action_confirm()
        self.assertEqual(self.record.state, 'confirmed')
    
    def test_compute_field(self):
        """Test campo computado"""
        self.record.line_ids = [(0, 0, {'subtotal': 100}), (0, 0, {'subtotal': 200})]
        self.assertEqual(self.record.total_amount, 300)
```

### Ejecutar Tests

```bash
# Todos los tests del módulo
python3 odoo-bin -c odoo.conf -d test_db -i pharmacy_base --test-enable --stop-after-init

# Test específico
python3 odoo-bin -c odoo.conf -d test_db --test-tags pharmacy_base.test_modelo

# Con coverage
coverage run --source=addons/pharmacy_base odoo-bin -c odoo.conf -d test_db --test-enable --stop-after-init
coverage report
```

---

## COMMITS Y GIT

### Formato de Commits

```
[TAG] modulo: descripción corta

Descripción detallada opcional en múltiples líneas
explicando el por qué del cambio.

Fixes #123
```

### Tags Disponibles

- `[ADD]` - Agregar nuevas funcionalidades
- `[FIX]` - Corrección de bugs
- `[IMP]` - Mejora de funcionalidades existentes
- `[REF]` - Refactorización de código
- `[REM]` - Eliminación de código/archivos
- `[REV]` - Revertir cambios previos
- `[MERGE]` - Merge de branches
- `[MOV]` - Mover o renombrar archivos
- `[I18N]` - Traducciones

### Ejemplos

```bash
[ADD] pharmacy_base: modelos de pacientes y prescriptores

Agrega los modelos res.partner extendidos para manejar
información de pacientes y médicos prescriptores con
sus respectivos campos específicos.

[FIX] pharmacy_pos: cálculo incorrecto de copago

El cálculo no consideraba el deducible cuando el paciente
había pagado una parte pero no todo el deducible anual.

[IMP] pharmacy_prescription: validación de interacciones

Mejora el sistema de detección de interacciones medicamentosas
usando una base de datos más completa y verificaciones cruzadas.
```

---

## DOCUMENTACIÓN

### Docstrings en Python

```python
def calculate_patient_cost(self, amount):
    """
    Calcula el costo que debe pagar el paciente según su plan de seguro.
    
    Considera el deducible anual, copago fijo y porcentaje de coseguro
    según la configuración del plan de seguro del paciente.
    
    Args:
        amount (float): Monto total del medicamento o servicio
    
    Returns:
        dict: Diccionario con las siguientes claves:
            - patient_pays (float): Monto que paga el paciente
            - insurance_pays (float): Monto que cubre el seguro
            - reason (str): Razón del cálculo aplicado
    
    Raises:
        UserError: Si la cobertura no está activa
    
    Examples:
        >>> insurance.calculate_patient_cost(1000.0)
        {'patient_pays': 250.0, 'insurance_pays': 750.0, 'reason': 'Coseguro 25%'}
    """
```

### README.md del Módulo

```markdown
# Pharmacy Base

## Descripción

Módulo base para el sistema de gestión de farmacias. Proporciona los modelos
fundamentales para productos farmacéuticos, pacientes, médicos y seguros.

## Características

- Clasificación de productos farmacéuticos
- Gestión de pacientes con historial médico
- Registro de médicos prescriptores
- Información de seguros médicos

## Instalación

1. Copiar el módulo a la carpeta de addons
2. Actualizar lista de aplicaciones
3. Instalar "Pharmacy Base"

## Configuración

### Categorías Farmacéuticas

Ir a: Farmacia > Configuración > Categorías Farmacéuticas

### Pacientes

Ir a: Farmacia > Maestros > Pacientes

## Uso

[Instrucciones de uso básico]

## Dependencias

- base
- product
- stock

## Autor

Tu Empresa - https://www.tuempresa.com

## Licencia

LGPL-3
```

---

## PERFORMANCE

### Buenas Prácticas

```python
# ❌ MAL: Búsqueda dentro de loop
for order in orders:
    partner = self.env['res.partner'].search([('id', '=', order.partner_id.id)])

# ✅ BIEN: Una sola búsqueda
partner_ids = orders.mapped('partner_id.id')
partners = self.env['res.partner'].browse(partner_ids)

# ❌ MAL: len(search())
total = len(self.env['pharmacy.prescription'].search([('state', '=', 'draft')]))

# ✅ BIEN: search_count()
total = self.env['pharmacy.prescription'].search_count([('state', '=', 'draft')])

# ❌ MAL: Loop sin mapped
total = 0
for line in order.line_ids:
    total += line.subtotal

# ✅ BIEN: Usar mapped y sum
total = sum(order.line_ids.mapped('subtotal'))

# ✅ BIEN: Usar SQL para operaciones masivas
self.env.cr.execute("""
    UPDATE pharmacy_prescription
    SET state = 'expired'
    WHERE expiration_date < %s AND state != 'expired'
""", (fields.Date.today(),))
```

### Indexar Campos

```python
# Campos que se buscan frecuentemente deben tener index=True
patient_code = fields.Char(index=True)
prescription_date = fields.Date(index=True)
```

---

## INTERNACIONALIZACIÓN

### Strings Traducibles

```python
from odoo import _

# ✅ Usar _() para strings visibles
raise UserError(_('No se puede eliminar un registro confirmado.'))

# ✅ En validaciones
@api.constrains('date')
def _check_date(self):
    if self.date < fields.Date.today():
        raise ValidationError(_('La fecha no puede ser pasada.'))
```

### XML Traducible

```xml
<field name="string" translate="1">Texto Traducible</field>
```

---

## CHECKLIST DE CALIDAD

Antes de considerar completado un módulo:

- [ ] Código sigue los estándares de nomenclatura
- [ ] Todos los campos tienen `string=`
- [ ] Campos relacionales tienen `ondelete=` explícito
- [ ] Tests tienen cobertura >70%
- [ ] No hay búsquedas dentro de loops
- [ ] Campos frecuentemente buscados están indexados
- [ ] Docstrings en métodos públicos
- [ ] README.md completo y actualizado
- [ ] Seguridad configurada (access y rules)
- [ ] Datos demo funcionales
- [ ] Sin errores en logs al instalar
- [ ] Sin warnings en logs al usar

---

**Mantén este documento como referencia constante durante el desarrollo.**
