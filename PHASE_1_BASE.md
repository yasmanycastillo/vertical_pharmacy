# FASE 1: MÓDULO BASE (pharmacy_base)

## OBJETIVO

Crear la infraestructura base que todos los demás módulos utilizarán. Este módulo contiene los modelos fundamentales, categorías y configuraciones base del sistema de farmacia.

---

## MODELOS A CREAR

### 1.1 `pharmacy.product.category`

Extiende `product.category` con clasificaciones farmacéuticas.

**Archivo:** `models/product_category.py`

```python
from odoo import models, fields, api

class PharmacyProductCategory(models.Model):
    _inherit = 'product.category'
    
    pharmaceutical_category = fields.Selection([
        ('prescription', 'Medicamento con Receta'),
        ('otc', 'Venta Libre (OTC)'),
        ('controlled', 'Medicamento Controlado'),
        ('dermocosmetica', 'Dermocosmética'),
        ('cuidado_personal', 'Cuidado Personal'),
        ('nutricion', 'Nutrición y Suplementos'),
        ('dispositivo_medico', 'Dispositivo Médico'),
        ('infantil', 'Cuidado Infantil'),
        ('ortopedia', 'Ortopedia y Primeros Auxilios'),
    ], string='Categoría Farmacéutica')
    
    requires_prescription = fields.Boolean(
        string='Requiere Receta',
        compute='_compute_requires_prescription',
        store=True
    )
    
    is_controlled = fields.Boolean(
        string='Medicamento Controlado',
        help='Requiere control especial y registro'
    )
    
    abc_classification = fields.Selection([
        ('A', 'Categoría A - Alta Rotación'),
        ('B', 'Categoría B - Rotación Media'),
        ('C', 'Categoría C - Baja Rotación'),
    ], string='Clasificación ABC', help='Clasificación por rotación de inventario')
    
    @api.depends('pharmaceutical_category')
    def _compute_requires_prescription(self):
        for record in self:
            record.requires_prescription = record.pharmaceutical_category in ['prescription', 'controlled']
```

---

### 1.2 `product.template` (Extensión)

Agrega campos farmacéuticos específicos a productos.

**Archivo:** `models/product_template.py`

```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Identificación Farmacéutica
    is_pharmaceutical = fields.Boolean(
        string='Es Producto Farmacéutico',
        default=False
    )
    
    active_principle = fields.Char(
        string='Principio Activo',
        help='Componente químico activo del medicamento'
    )
    
    pharmaceutical_form = fields.Selection([
        ('tableta', 'Tableta/Comprimido'),
        ('capsula', 'Cápsula'),
        ('jarabe', 'Jarabe'),
        ('suspension', 'Suspensión'),
        ('solucion', 'Solución'),
        ('crema', 'Crema/Pomada'),
        ('gel', 'Gel'),
        ('inyectable', 'Inyectable'),
        ('supositorio', 'Supositorio'),
        ('inhalador', 'Inhalador'),
        ('gotas', 'Gotas'),
        ('parche', 'Parche Transdérmico'),
        ('otro', 'Otro'),
    ], string='Forma Farmacéutica')
    
    concentration = fields.Char(
        string='Concentración',
        help='Ej: "500mg", "250mg/5ml"'
    )
    
    presentation = fields.Char(
        string='Presentación',
        help='Ej: "Caja con 20 tabletas", "Frasco 120ml"'
    )
    
    # Nomenclatura
    generic_name = fields.Char(
        string='Nombre Genérico',
        help='Denominación Común Internacional (DCI)'
    )
    
    brand_name = fields.Char(
        string='Nombre Comercial/Marca'
    )
    
    laboratory_id = fields.Many2one(
        'res.partner',
        string='Laboratorio',
        domain=[('is_laboratory', '=', True)]
    )
    
    therapeutic_class = fields.Char(
        string='Clase Terapéutica',
        help='Ej: "Analgésico", "Antibiótico", "Antihipertensivo"'
    )
    
    # Condiciones de Almacenamiento
    requires_refrigeration = fields.Boolean(
        string='Requiere Refrigeración',
        default=False
    )
    
    photosensitive = fields.Boolean(
        string='Fotosensible',
        help='Requiere protección de la luz',
        default=False
    )
    
    # Información Clínica
    contraindications = fields.Text(
        string='Contraindicaciones'
    )
    
    side_effects = fields.Text(
        string='Efectos Secundarios'
    )
    
    dosage_instructions = fields.Text(
        string='Instrucciones de Dosificación'
    )
    
    # Productos Relacionados (Cross-Selling)
    related_products_ids = fields.Many2many(
        'product.template',
        'product_related_rel',
        'product_id',
        'related_product_id',
        string='Productos Relacionados',
        help='Productos que se sugieren comprar juntos'
    )
    
    # Campos Relacionados
    requires_prescription = fields.Boolean(
        string='Requiere Receta',
        related='categ_id.requires_prescription',
        store=True,
        readonly=True
    )
    
    @api.constrains('is_pharmaceutical', 'active_principle')
    def _check_pharmaceutical_fields(self):
        for record in self:
            if record.is_pharmaceutical and not record.active_principle:
                raise ValidationError(_('Los productos farmacéuticos deben tener un principio activo definido.'))
    
    @api.onchange('is_pharmaceutical')
    def _onchange_is_pharmaceutical(self):
        if self.is_pharmaceutical and not self.categ_id.pharmaceutical_category:
            return {
                'warning': {
                    'title': _('Advertencia'),
                    'message': _('Asegúrese de seleccionar una categoría farmacéutica apropiada.')
                }
            }
```

---

### 1.3 `res.partner` (Extensión)

Agrega campos para pacientes, médicos y laboratorios.

**Archivo:** `models/res_partner.py`

```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Tipos de Partner
    is_patient = fields.Boolean(
        string='Es Paciente',
        default=False
    )
    
    is_prescriber = fields.Boolean(
        string='Es Médico Prescriptor',
        default=False
    )
    
    is_laboratory = fields.Boolean(
        string='Es Laboratorio',
        default=False
    )
    
    # Información de Paciente
    patient_code = fields.Char(
        string='Código de Paciente',
        copy=False,
        readonly=True,
        help='Código único generado automáticamente'
    )
    
    allergies = fields.Text(
        string='Alergias Conocidas',
        help='Alergias a medicamentos o componentes'
    )
    
    chronic_conditions = fields.Text(
        string='Condiciones Crónicas',
        help='Enfermedades crónicas o de largo plazo'
    )
    
    current_medications = fields.Text(
        string='Medicamentos Actuales',
        help='Medicamentos que toma actualmente'
    )
    
    # Información de Médico Prescriptor
    medical_license = fields.Char(
        string='Cédula Profesional',
        help='Número de licencia médica'
    )
    
    prescriber_specialty = fields.Selection([
        ('general', 'Medicina General'),
        ('pediatrics', 'Pediatría'),
        ('cardiology', 'Cardiología'),
        ('dermatology', 'Dermatología'),
        ('gynecology', 'Ginecología'),
        ('orthopedics', 'Ortopedia'),
        ('psychiatry', 'Psiquiatría'),
        ('ophthalmology', 'Oftalmología'),
        ('other', 'Otra Especialidad'),
    ], string='Especialidad Médica')
    
    prescriber_signature = fields.Binary(
        string='Firma Digitalizada',
        help='Firma del médico para recetas'
    )
    
    # Relaciones
    insurance_info_ids = fields.One2many(
        'pharmacy.insurance.info',
        'partner_id',
        string='Información de Seguros'
    )
    
    prescription_history_ids = fields.One2many(
        'pharmacy.prescription',
        'patient_id',
        string='Historial de Recetas'
    )
    
    # Constraints
    _sql_constraints = [
        ('medical_license_unique', 'UNIQUE(medical_license)', 
         'La cédula profesional debe ser única.'),
        ('patient_code_unique', 'UNIQUE(patient_code)', 
         'El código de paciente debe ser único.'),
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_patient') and not vals.get('patient_code'):
                vals['patient_code'] = self.env['ir.sequence'].next_by_code('pharmacy.patient.code')
        return super().create(vals_list)
    
    @api.constrains('is_prescriber', 'medical_license')
    def _check_prescriber_license(self):
        for record in self:
            if record.is_prescriber and not record.medical_license:
                raise ValidationError(_('Los médicos prescriptores deben tener una cédula profesional registrada.'))
```

---

### 1.4 `pharmacy.insurance.info`

Información de seguros médicos del paciente.

**Archivo:** `models/insurance_info.py`

```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class PharmacyInsuranceInfo(models.Model):
    _name = 'pharmacy.insurance.info'
    _description = 'Información de Seguro Médico del Paciente'
    _order = 'start_date desc'
    
    # Relaciones
    partner_id = fields.Many2one(
        'res.partner',
        string='Paciente',
        required=True,
        domain=[('is_patient', '=', True)],
        ondelete='cascade'
    )
    
    insurance_company_id = fields.Many2one(
        'res.partner',
        string='Aseguradora',
        required=True,
        domain=[('is_company', '=', True)],
        help='Compañía de seguros'
    )
    
    # Información de la Póliza
    policy_number = fields.Char(
        string='Número de Póliza',
        required=True
    )
    
    member_id = fields.Char(
        string='ID del Asegurado',
        required=True
    )
    
    group_number = fields.Char(
        string='Número de Grupo'
    )
    
    plan_name = fields.Char(
        string='Nombre del Plan',
        required=True,
        help='Ej: "Plan Básico", "Plan Premium"'
    )
    
    coverage_level = fields.Selection([
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('premium', 'Premium'),
    ], string='Nivel de Cobertura', default='basico')
    
    # Vigencia
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    start_date = fields.Date(
        string='Fecha de Inicio',
        required=True,
        default=fields.Date.today
    )
    
    end_date = fields.Date(
        string='Fecha de Fin'
    )
    
    # Costos
    copay_default = fields.Monetary(
        string='Copago por Defecto',
        currency_field='currency_id',
        help='Monto fijo que paga el paciente por medicamento'
    )
    
    coinsurance_percentage = fields.Float(
        string='Porcentaje de Coseguro',
        help='Porcentaje que paga el paciente (ej: 20%)'
    )
    
    annual_deductible = fields.Monetary(
        string='Deducible Anual',
        currency_field='currency_id',
        help='Monto anual que el paciente debe pagar antes de que el seguro cubra'
    )
    
    deductible_met = fields.Monetary(
        string='Deducible Pagado',
        currency_field='currency_id',
        help='Monto del deducible ya pagado en el año actual'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id
    )
    
    # Notas
    notes = fields.Text(
        string='Notas'
    )
    
    # Campos Computados
    is_valid = fields.Boolean(
        string='Cobertura Válida',
        compute='_compute_is_valid',
        store=False
    )
    
    remaining_deductible = fields.Monetary(
        string='Deducible Restante',
        compute='_compute_remaining_deductible',
        currency_field='currency_id'
    )
    
    @api.depends('active', 'start_date', 'end_date')
    def _compute_is_valid(self):
        today = date.today()
        for record in self:
            if not record.active:
                record.is_valid = False
            elif record.end_date and record.end_date < today:
                record.is_valid = False
            elif record.start_date > today:
                record.is_valid = False
            else:
                record.is_valid = True
    
    @api.depends('annual_deductible', 'deductible_met')
    def _compute_remaining_deductible(self):
        for record in self:
            record.remaining_deductible = record.annual_deductible - record.deductible_met
    
    def calculate_patient_cost(self, amount):
        """
        Calcula el costo que debe pagar el paciente según su plan
        
        :param amount: Monto total del medicamento
        :return: dict con {'patient_pays': X, 'insurance_pays': Y}
        """
        self.ensure_one()
        
        if not self.is_valid:
            return {
                'patient_pays': amount,
                'insurance_pays': 0.0,
                'reason': 'Cobertura no válida'
            }
        
        # Si hay deducible pendiente
        if self.remaining_deductible > 0:
            if amount <= self.remaining_deductible:
                return {
                    'patient_pays': amount,
                    'insurance_pays': 0.0,
                    'reason': 'Aplicado a deducible'
                }
            else:
                amount_after_deductible = amount - self.remaining_deductible
                patient_pays = self.remaining_deductible
        else:
            amount_after_deductible = amount
            patient_pays = 0.0
        
        # Aplicar copago o coseguro
        if self.copay_default > 0:
            patient_pays += self.copay_default
        elif self.coinsurance_percentage > 0:
            patient_pays += amount_after_deductible * (self.coinsurance_percentage / 100.0)
        
        insurance_pays = amount - patient_pays
        
        return {
            'patient_pays': patient_pays,
            'insurance_pays': insurance_pays,
            'reason': 'Cálculo normal'
        }
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise ValidationError(_('La fecha de fin no puede ser anterior a la fecha de inicio.'))
    
    _sql_constraints = [
        ('policy_member_unique', 'UNIQUE(insurance_company_id, policy_number, member_id)',
         'Ya existe un registro con esta combinación de aseguradora, póliza y miembro.')
    ]
```

---

## VISTAS A CREAR

### 2.1 Vista de Producto Farmacéutico

**Archivo:** `views/product_template_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Vista de formulario extendida -->
    <record id="product_template_form_view_pharmacy" model="ir.ui.view">
        <field name="name">product.template.form.pharmacy</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_only_form_view"/>
        <field name="arch" type="xml">
            <!-- Agregar checkbox en la parte superior -->
            <field name="name" position="before">
                <field name="is_pharmaceutical"/>
            </field>
            
            <!-- Agregar página de Información Farmacéutica -->
            <xpath expr="//notebook" position="inside">
                <page string="Información Farmacéutica" attrs="{'invisible': [('is_pharmaceutical', '=', False)]}">
                    <group>
                        <group string="Identificación">
                            <field name="generic_name"/>
                            <field name="brand_name"/>
                            <field name="active_principle" required="1"/>
                            <field name="pharmaceutical_form"/>
                            <field name="concentration"/>
                            <field name="presentation"/>
                        </group>
                        <group string="Fabricante">
                            <field name="laboratory_id"/>
                            <field name="therapeutic_class"/>
                            <field name="requires_prescription" readonly="1"/>
                        </group>
                    </group>
                    
                    <group string="Condiciones de Almacenamiento">
                        <group>
                            <field name="requires_refrigeration"/>
                            <field name="photosensitive"/>
                        </group>
                    </group>
                    
                    <group string="Información Clínica">
                        <field name="dosage_instructions" placeholder="Ej: Tomar 1 tableta cada 8 horas con alimentos"/>
                        <field name="contraindications" placeholder="Situaciones en las que NO debe usarse este medicamento"/>
                        <field name="side_effects" placeholder="Efectos secundarios comunes y graves"/>
                    </group>
                    
                    <group string="Productos Relacionados (Cross-Selling)">
                        <field name="related_products_ids" widget="many2many_tags" nolabel="1"/>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### 2.2 Vista de Pacientes

**Archivo:** `views/res_partner_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Vista de formulario para pacientes -->
    <record id="res_partner_form_view_pharmacy_patient" model="ir.ui.view">
        <field name="name">res.partner.form.pharmacy.patient</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <!-- Agregar checkboxes en la parte superior -->
            <field name="company_type" position="after">
                <field name="is_patient"/>
                <field name="is_prescriber"/>
                <field name="is_laboratory"/>
            </field>
            
            <!-- Información de Paciente -->
            <xpath expr="//notebook" position="inside">
                <page string="Información del Paciente" attrs="{'invisible': [('is_patient', '=', False)]}">
                    <group>
                        <group>
                            <field name="patient_code" readonly="1"/>
                        </group>
                    </group>
                    <group string="Información Médica">
                        <field name="allergies" placeholder="Ej: Penicilina, Aspirina, Sulfas"/>
                        <field name="chronic_conditions" placeholder="Ej: Diabetes, Hipertensión, Asma"/>
                        <field name="current_medications" placeholder="Medicamentos que toma regularmente"/>
                    </group>
                    <group string="Seguros Médicos">
                        <field name="insurance_info_ids" nolabel="1">
                            <tree>
                                <field name="insurance_company_id"/>
                                <field name="policy_number"/>
                                <field name="plan_name"/>
                                <field name="is_valid" widget="boolean"/>
                                <field name="start_date"/>
                                <field name="end_date"/>
                            </tree>
                        </field>
                    </group>
                </page>
                
                <!-- Información de Médico Prescriptor -->
                <page string="Información del Prescriptor" attrs="{'invisible': [('is_prescriber', '=', False)]}">
                    <group>
                        <group>
                            <field name="medical_license" required="1"/>
                            <field name="prescriber_specialty"/>
                        </group>
                        <group>
                            <field name="prescriber_signature" widget="image" class="oe_avatar"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
    
    <!-- Acción para Pacientes -->
    <record id="action_pharmacy_patients" model="ir.actions.act_window">
        <field name="name">Pacientes</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">kanban,tree,form</field>
        <field name="domain">[('is_patient', '=', True)]</field>
        <field name="context">{'default_is_patient': True}</field>
    </record>
    
    <!-- Acción para Médicos Prescriptores -->
    <record id="action_pharmacy_prescribers" model="ir.actions.act_window">
        <field name="name">Médicos Prescriptores</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form</field>
        <field name="domain">[('is_prescriber', '=', True)]</field>
        <field name="context">{'default_is_prescriber': True}</field>
    </record>
    
    <!-- Acción para Laboratorios -->
    <record id="action_pharmacy_laboratories" model="ir.actions.act_window">
        <field name="name">Laboratorios</field>
        <field name="res_model">res.partner</field>
        <field name="view_mode">tree,form</field>
        <field name="domain">[('is_laboratory', '=', True)]</field>
        <field name="context">{'default_is_laboratory': True, 'default_is_company': True}</field>
    </record>
</odoo>
```

### 2.3 Vista de Información de Seguros

**Archivo:** `views/insurance_info_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="pharmacy_insurance_info_form_view" model="ir.ui.view">
        <field name="name">pharmacy.insurance.info.form</field>
        <field name="model">pharmacy.insurance.info</field>
        <field name="arch" type="xml">
            <form string="Información de Seguro">
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="toggle_active" type="object" class="oe_stat_button" icon="fa-check">
                            <field name="active" widget="boolean_button" options="{'terminology': 'active'}"/>
                        </button>
                    </div>
                    <group>
                        <group string="Paciente y Aseguradora">
                            <field name="partner_id" options="{'no_create': True}"/>
                            <field name="insurance_company_id" options="{'no_create': True}"/>
                        </group>
                        <group string="Información de la Póliza">
                            <field name="policy_number"/>
                            <field name="member_id"/>
                            <field name="group_number"/>
                            <field name="plan_name"/>
                            <field name="coverage_level"/>
                        </group>
                    </group>
                    <group string="Vigencia">
                        <group>
                            <field name="start_date"/>
                            <field name="end_date"/>
                        </group>
                        <group>
                            <field name="is_valid" widget="boolean"/>
                        </group>
                    </group>
                    <group string="Costos">
                        <group>
                            <field name="currency_id" invisible="1"/>
                            <field name="copay_default" widget="monetary"/>
                            <field name="coinsurance_percentage" widget="percentage"/>
                        </group>
                        <group>
                            <field name="annual_deductible" widget="monetary"/>
                            <field name="deductible_met" widget="monetary"/>
                            <field name="remaining_deductible" widget="monetary"/>
                        </group>
                    </group>
                    <group string="Notas">
                        <field name="notes" nolabel="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    
    <record id="pharmacy_insurance_info_tree_view" model="ir.ui.view">
        <field name="name">pharmacy.insurance.info.tree</field>
        <field name="model">pharmacy.insurance.info</field>
        <field name="arch" type="xml">
            <tree string="Seguros Médicos">
                <field name="partner_id"/>
                <field name="insurance_company_id"/>
                <field name="policy_number"/>
                <field name="plan_name"/>
                <field name="is_valid" widget="boolean"/>
                <field name="start_date"/>
                <field name="end_date"/>
                <field name="copay_default" widget="monetary"/>
                <field name="active" invisible="1"/>
            </tree>
        </field>
    </record>
</odoo>
```

---

## MENÚS

**Archivo:** `views/menus.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Menú Principal de Farmacia -->
    <menuitem id="menu_pharmacy_root"
              name="Farmacia"
              sequence="10"
              web_icon="pharmacy_base,static/description/icon.png"/>
    
    <!-- Submenú: Maestros -->
    <menuitem id="menu_pharmacy_masters"
              name="Maestros"
              parent="menu_pharmacy_root"
              sequence="10"/>
    
    <menuitem id="menu_pharmacy_products"
              name="Productos Farmacéuticos"
              parent="menu_pharmacy_masters"
              action="product.product_template_action"
              sequence="10"/>
    
    <menuitem id="menu_pharmacy_patients"
              name="Pacientes"
              parent="menu_pharmacy_masters"
              action="action_pharmacy_patients"
              sequence="20"/>
    
    <menuitem id="menu_pharmacy_prescribers"
              name="Médicos Prescriptores"
              parent="menu_pharmacy_masters"
              action="action_pharmacy_prescribers"
              sequence="30"/>
    
    <!-- Submenú: Configuración -->
    <menuitem id="menu_pharmacy_configuration"
              name="Configuración"
              parent="menu_pharmacy_root"
              sequence="100"/>
    
    <menuitem id="menu_pharmacy_categories"
              name="Categorías Farmacéuticas"
              parent="menu_pharmacy_configuration"
              action="product.product_category_action_form"
              sequence="10"/>
    
    <menuitem id="menu_pharmacy_laboratories"
              name="Laboratorios"
              parent="menu_pharmacy_configuration"
              action="action_pharmacy_laboratories"
              sequence="20"/>
</odoo>
```

---

## SEGURIDAD

**Archivo:** `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_pharmacy_insurance_info_user,pharmacy.insurance.info user,model_pharmacy_insurance_info,pharmacy_group_user,1,1,1,0
access_pharmacy_insurance_info_pharmacist,pharmacy.insurance.info pharmacist,model_pharmacy_insurance_info,pharmacy_group_pharmacist,1,1,1,1
access_pharmacy_insurance_info_manager,pharmacy.insurance.info manager,model_pharmacy_insurance_info,pharmacy_group_manager,1,1,1,1
```

**Archivo:** `security/security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <!-- Grupos de Acceso -->
        <record id="pharmacy_group_user" model="res.groups">
            <field name="name">Farmacia: Usuario</field>
            <field name="category_id" ref="base.module_category_pharmacy"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>
        
        <record id="pharmacy_group_pharmacist" model="res.groups">
            <field name="name">Farmacia: Farmacéutico</field>
            <field name="category_id" ref="base.module_category_pharmacy"/>
            <field name="implied_ids" eval="[(4, ref('pharmacy_group_user'))]"/>
        </record>
        
        <record id="pharmacy_group_manager" model="res.groups">
            <field name="name">Farmacia: Gerente</field>
            <field name="category_id" ref="base.module_category_pharmacy"/>
            <field name="implied_ids" eval="[(4, ref('pharmacy_group_pharmacist'))]"/>
        </record>
    </data>
</odoo>
```

---

## DATOS Y SECUENCIAS

**Archivo:** `data/sequences.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Secuencia para Código de Paciente -->
        <record id="seq_pharmacy_patient_code" model="ir.sequence">
            <field name="name">Código de Paciente</field>
            <field name="code">pharmacy.patient.code</field>
            <field name="prefix">PAC</field>
            <field name="padding">6</field>
            <field name="number_next">1</field>
            <field name="number_increment">1</field>
        </record>
    </data>
</odoo>
```

---

## DATOS DEMO

**Archivo:** `demo/demo.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Categorías Farmacéuticas Demo -->
        <record id="categ_medicamentos_receta" model="product.category">
            <field name="name">Medicamentos con Receta</field>
            <field name="pharmaceutical_category">prescription</field>
            <field name="abc_classification">A</field>
        </record>
        
        <record id="categ_medicamentos_otc" model="product.category">
            <field name="name">Medicamentos de Venta Libre</field>
            <field name="pharmaceutical_category">otc</field>
            <field name="abc_classification">B</field>
        </record>
        
        <!-- Laboratorios Demo -->
        <record id="laboratory_farmalab" model="res.partner">
            <field name="name">Laboratorios FarmaLab S.A.</field>
            <field name="is_company">True</field>
            <field name="is_laboratory">True</field>
        </record>
        
        <!-- Aseguradoras Demo -->
        <record id="insurance_salud_total" model="res.partner">
            <field name="name">Salud Total S.A.</field>
            <field name="is_company">True</field>
        </record>
        
        <!-- Médicos Demo -->
        <record id="prescriber_dr_garcia" model="res.partner">
            <field name="name">Dr. Carlos García</field>
            <field name="is_prescriber">True</field>
            <field name="medical_license">MED-12345</field>
            <field name="prescriber_specialty">general</field>
        </record>
        
        <!-- Pacientes Demo -->
        <record id="patient_maria_lopez" model="res.partner">
            <field name="name">María López</field>
            <field name="is_patient">True</field>
            <field name="allergies">Penicilina</field>
            <field name="chronic_conditions">Diabetes Tipo 2</field>
        </record>
        
        <!-- Productos Farmacéuticos Demo -->
        <record id="product_ibuprofeno_400" model="product.template">
            <field name="name">Ibuprofeno 400mg</field>
            <field name="is_pharmaceutical">True</field>
            <field name="categ_id" ref="categ_medicamentos_otc"/>
            <field name="active_principle">Ibuprofeno</field>
            <field name="pharmaceutical_form">tableta</field>
            <field name="concentration">400mg</field>
            <field name="presentation">Caja con 20 tabletas</field>
            <field name="generic_name">Ibuprofeno</field>
            <field name="therapeutic_class">Analgésico/Antiinflamatorio</field>
            <field name="list_price">150.00</field>
            <field name="standard_price">75.00</field>
            <field name="type">product</field>
        </record>
    </data>
</odoo>
```

---

## MANIFEST

**Archivo:** `__manifest__.py`

```python
{
    'name': 'Pharmacy Base',
    'version': '18.0.1.0.0',
    'category': 'Healthcare/Pharmacy',
    'summary': 'Módulo base para gestión de farmacias',
    'description': """
        Pharmacy Base Module
        ====================
        Proporciona la infraestructura base para el sistema de farmacia:
        * Categorías y productos farmacéuticos
        * Gestión de pacientes y médicos prescriptores
        * Información de seguros médicos
        * Laboratorios farmacéuticos
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/insurance_info_views.xml',
        'views/menus.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

---

## TESTS

**Archivo:** `tests/test_product_template.py`

```python
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestProductTemplate(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env['product.template']
        self.category = self.env['product.category'].create({
            'name': 'Test Pharma Category',
            'pharmaceutical_category': 'prescription',
        })
    
    def test_pharmaceutical_product_requires_active_principle(self):
        """Test que productos farmacéuticos requieren principio activo"""
        with self.assertRaises(ValidationError):
            self.ProductTemplate.create({
                'name': 'Test Product',
                'is_pharmaceutical': True,
                'categ_id': self.category.id,
                # Falta active_principle
            })
    
    def test_create_pharmaceutical_product_success(self):
        """Test creación exitosa de producto farmacéutico"""
        product = self.ProductTemplate.create({
            'name': 'Test Pharma Product',
            'is_pharmaceutical': True,
            'active_principle': 'Paracetamol',
            'categ_id': self.category.id,
        })
        self.assertTrue(product.requires_prescription)
        self.assertEqual(product.active_principle, 'Paracetamol')
```

**Archivo:** `tests/test_res_partner.py`

```python
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestResPartner(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
    
    def test_patient_code_auto_generated(self):
        """Test que el código de paciente se genera automáticamente"""
        patient = self.Partner.create({
            'name': 'Test Patient',
            'is_patient': True,
        })
        self.assertTrue(patient.patient_code)
        self.assertTrue(patient.patient_code.startswith('PAC'))
    
    def test_prescriber_requires_license(self):
        """Test que médicos prescriptores requieren licencia"""
        with self.assertRaises(ValidationError):
            self.Partner.create({
                'name': 'Test Doctor',
                'is_prescriber': True,
                # Falta medical_license
            })
```

---

## CRITERIOS DE ACEPTACIÓN FASE 1

- [ ] Módulo `pharmacy_base` se instala sin errores
- [ ] Productos pueden marcarse como farmacéuticos
- [ ] Productos farmacéuticos tienen todos los campos específicos
- [ ] Validación de principio activo funciona
- [ ] Categorías farmacéuticas configurables
- [ ] Pacientes registrables con código automático
- [ ] Médicos requieren cédula profesional
- [ ] Información de seguros completa y funcional
- [ ] Cálculo de copago funciona correctamente
- [ ] Menús visibles y funcionales
- [ ] Datos demo se cargan correctamente
- [ ] Tests pasan al 100%
- [ ] Grupos de seguridad funcionan
- [ ] Documentación completa en README.md

---

**¡Comienza el desarrollo!** Una vez completada esta fase, continúa con `PHASE_2_POS.md`.
