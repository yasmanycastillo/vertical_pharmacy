# DESARROLLO MÓDULO FARMACIA ODOO 18

## CONTEXTO DEL PROYECTO

Eres un desarrollador experto en Odoo 18 especializado en el desarrollo de módulos verticales para el sector salud. Tu tarea es desarrollar un módulo completo de Farmacia que extienda las capacidades estándar de Odoo para adaptarse a las necesidades específicas del sector farmacéutico.

**Ruta de Odoo Core:** `~/src/odoo/core/addons`

**Enfoque de Desarrollo:** Incremental con entregables validables en cada fase.

**Volumen Esperado:** Sistema escalable para 2-50+ sucursales, soportando hasta 10,000 transacciones diarias.

---

## ARQUITECTURA GENERAL DEL MÓDULO

### Estructura de Módulos

Desarrollarás un ecosistema modular compuesto por:

1. **`pharmacy_base`** - Módulo base con modelos y funcionalidades core
2. **`pharmacy_pos`** - Extensión del POS estándar de Odoo (PRIORIDAD 1)
3. **`pharmacy_insurance`** - Sistema de copago y seguros (PRIORIDAD 2)
4. **`pharmacy_prescription`** - Gestión de recetas médicas (PRIORIDAD 3)
5. **`pharmacy_delivery`** - Sistema de entregas a domicilio (PRIORIDAD 4)
6. **`pharmacy_stock_enhanced`** - Mejoras de inventario farmacéutico (PRIORIDAD 5)

### Dependencias entre Módulos

```
pharmacy_base (core)
    ├── pharmacy_pos (depende de: point_of_sale, pharmacy_base)
    ├── pharmacy_insurance (depende de: pharmacy_base, pharmacy_pos)
    ├── pharmacy_prescription (depende de: pharmacy_base, pharmacy_pos)
    ├── pharmacy_delivery (depende de: sale, pharmacy_base, pharmacy_prescription)
    └── pharmacy_stock_enhanced (depende de: stock, pharmacy_base)
```

---

## FASE 1: MÓDULO BASE (`pharmacy_base`)

### Objetivo
Crear la infraestructura base que todos los demás módulos utilizarán.

### Modelos a Crear

#### 1.1 `pharmacy.product.category`
Extiende `product.category` con clasificaciones farmacéuticas:

```python
# Campos adicionales:
- pharmaceutical_category: Selection [
    ('prescription', 'Medicamento con Receta'),
    ('otc', 'Venta Libre (OTC)'),
    ('controlled', 'Medicamento Controlado'),
    ('dermocosmetica', 'Dermocosmética'),
    ('cuidado_personal', 'Cuidado Personal'),
    ('nutricion', 'Nutrición y Suplementos'),
    ('dispositivo_medico', 'Dispositivo Médico'),
    ('infantil', 'Cuidado Infantil'),
    ('ortopedia', 'Ortopedia y Primeros Auxilios')
]
- requires_prescription: Boolean (automático según pharmaceutical_category)
- is_controlled: Boolean
- abc_classification: Selection ['A', 'B', 'C'] (rotación de inventario)
```

#### 1.2 `product.template` (Extensión)
Agrega campos farmacéuticos específicos:

```python
# Campos nuevos:
- is_pharmaceutical: Boolean
- active_principle: Char (Principio Activo)
- pharmaceutical_form: Selection [
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
    ('otro', 'Otro')
]
- concentration: Char (ej: "500mg", "250mg/5ml")
- presentation: Char (ej: "Caja con 20 tabletas", "Frasco 120ml")
- generic_name: Char (nombre genérico del medicamento)
- brand_name: Char (nombre comercial)
- laboratory: Many2one a res.partner (filtrado por is_laboratory=True)
- therapeutic_class: Char (clase terapéutica)
- requires_refrigeration: Boolean
- photosensitive: Boolean (requiere protección de luz)
- contraindications: Text
- side_effects: Text
- dosage_instructions: Text
- related_products: Many2many (productos que se sugieren comprar juntos)

# Métodos:
- _compute_requires_prescription(): basado en pharmaceutical_category
- _check_stock_pharmacy_rules(): validaciones específicas
```
- Nota: pharmaceutical_form podrias enlazarlo con las unidades de medida

#### 1.3 `res.partner` (Extensión)
Agrega campos para pacientes, médicos y laboratorios:

```python
# Campos nuevos:
- is_patient: Boolean
- is_prescriber: Boolean (médico)
- is_laboratory: Boolean
- patient_code: Char (código único de paciente, secuencia automática)
- medical_license: Char (cédula profesional del médico)
- prescriber_specialty: Selection (especialidad médica)
- prescriber_signature: Binary (firma digitalizada)
- allergies: Text (alergias del paciente)
- chronic_conditions: Text (condiciones crónicas)
- current_medications: Text (medicamentos actuales)
- insurance_info_ids: One2many a pharmacy.insurance.info
- prescription_history_ids: One2many a pharmacy.prescription

# Constraints:
- medical_license único si is_prescriber=True
- patient_code único si is_patient=True
```

#### 1.4 `pharmacy.insurance.info`
Información de seguros del paciente:

```python
# Campos:
- partner_id: Many2one a res.partner (paciente)
- insurance_company_id: Many2one a res.partner (aseguradora)
- policy_number: Char (número de póliza)
- member_id: Char (ID del asegurado)
- group_number: Char
- plan_name: Char (nombre del plan)
- coverage_level: Selection ['basico', 'intermedio', 'premium']
- active: Boolean
- start_date: Date
- end_date: Date
- copay_default: Float (copago por defecto)
- coinsurance_percentage: Float (% de coseguro)
- annual_deductible: Float
- deductible_met: Float (deducible ya pagado en el año)
- notes: Text

# Métodos:
- _check_coverage_validity(): verifica si la cobertura está activa
- calculate_patient_cost(amount): calcula copago/coseguro
```

### Vistas a Crear

1. **Vista de formulario de producto farmacéutico** con tabs:
   - Información General
   - Información Farmacéutica (activo, forma, concentración)
   - Indicaciones y Contraindicaciones
   - Control de Stock (lotes, caducidad)
   - Productos Relacionados

2. **Vista de pacientes** con información médica y seguros

3. **Vista de prescriptores** con licencia y firma

4. **Menú de configuración:**
   ```
   Farmacia
   ├── Configuración
   │   ├── Categorías Farmacéuticas
   │   ├── Laboratorios
   │   └── Aseguradoras
   ├── Maestros
   │   ├── Productos Farmacéuticos
   │   ├── Pacientes
   │   └── Médicos Prescriptores
   ```

### Seguridad

Crear grupos de acceso:
- `pharmacy_user`: Usuario básico (vendedor)
- `pharmacy_pharmacist`: Farmacéutico (puede validar recetas)
- `pharmacy_manager`: Gerente (acceso completo)

### Datos Demo

Crear datos de demostración:
- 5 categorías farmacéuticas pre-configuradas
- 20 productos farmacéuticos de ejemplo
- 10 pacientes de ejemplo
- 5 médicos prescriptores
- 3 planes de seguro

### Entregable Fase 1

**Criterios de Aceptación:**
- [ ] Módulo `pharmacy_base` instalable sin errores
- [ ] Productos pueden clasificarse como farmacéuticos con toda su información
- [ ] Pacientes y médicos registrables con campos específicos
- [ ] Información de seguros configurable por paciente
- [ ] Menús de configuración funcionales
- [ ] Datos demo cargables
- [ ] Tests unitarios básicos (al menos 10 tests)

---

## FASE 2: POS ESPECIALIZADO (`pharmacy_pos`)

### Objetivo
Adaptar el POS de Odoo para ventas farmacéuticas con validaciones específicas, gestión de recetas y copagos.

### Modelos a Crear/Extender

#### 2.1 `pos.config` (Extensión)
```python
# Campos nuevos:
- is_pharmacy_pos: Boolean
- allow_prescription_sales: Boolean
- require_pharmacist_validation: Boolean
- auto_apply_insurance: Boolean
- show_patient_history: Boolean
- allow_otc_without_patient: Boolean
- default_insurance_journal_id: Many2one a account.journal (diario para seguros)
```

#### 2.2 `pos.order` (Extensión)
```python
# Campos nuevos:
- patient_id: Many2one a res.partner (domain: is_patient=True)
- prescription_id: Many2one a pharmacy.prescription
- pharmacist_id: Many2one a res.users (farmacéutico que validó)
- has_prescription_items: Boolean (computed)
- total_insurance_amount: Monetary (monto cubierto por seguro)
- total_copay_amount: Monetary (copago del paciente)
- insurance_claim_reference: Char (referencia de reclamación)
- validation_state: Selection ['pending', 'validated', 'rejected']

# Métodos:
- _calculate_insurance_amounts(): calcula copagos por línea
- _validate_prescription_items(): valida que items con receta tengan prescripción válida
- _check_patient_required(): verifica si se requiere paciente
```

#### 2.3 `pos.order.line` (Extensión)
```python
# Campos nuevos:
- requires_prescription: Boolean (related de product_id)
- prescription_line_id: Many2one a pharmacy.prescription.line
- insurance_covered: Boolean
- insurance_amount: Monetary (monto cubierto por seguro)
- copay_amount: Monetary (copago del paciente)
- patient_pays: Monetary (computed: price_subtotal - insurance_amount)
- dispensed_quantity: Float (cantidad realmente dispensada)
- lot_id: Many2one a stock.lot (lote dispensado)

# Métodos:
- _compute_insurance_amounts(): calcula copago según plan del paciente
```

#### 2.4 `pos.payment` (Extensión)
```python
# Campos nuevos:
- payment_type: Selection ['patient', 'insurance'] (quién paga)
- insurance_company_id: Many2one a res.partner (si payment_type='insurance')
```

### Funcionalidad JavaScript/OWL (POS Frontend)

#### 2.5 Pantalla de Selección de Paciente
Crear componente `PatientSelectionScreen`:

```javascript
// Funcionalidades:
- Búsqueda de pacientes por nombre, código, identificación
- Mostrar información de seguros activos del paciente
- Mostrar alergias y condiciones (ALERTAS VISUALES)
- Botón "Crear Paciente Rápido" para ventas OTC
- Botón "Continuar sin Paciente" (solo si allow_otc_without_patient=True)
- Historial de compras del paciente (últimas 10)
```

#### 2.6 Validación de Recetas en POS
Modificar `ProductScreen`:

```javascript
// Al agregar producto con requires_prescription=True:
1. Verificar si hay paciente seleccionado
2. Verificar si hay receta asociada a la orden
3. Mostrar modal de validación de receta
4. Validar que el producto esté en la receta
5. Validar cantidad prescrita vs. cantidad a dispensar
6. Permitir dispensación parcial con justificación
7. Requerir validación de farmacéutico (si está configurado)
```

#### 2.7 Cálculo Automático de Copagos
Modificar `PaymentScreen`:

```javascript
// Antes de mostrar pantalla de pago:
1. Calcular por cada línea el monto cubierto por seguro
2. Calcular copago del paciente por línea
3. Mostrar desglose visual:
   - Subtotal: $XXX
   - Cobertura Seguro: -$XXX
   - Copago Paciente: $XXX
4. Generar dos pagos automáticos:
   - Pago 1: Copago (método efectivo/tarjeta)
   - Pago 2: Seguro (método "Seguro Médico", pendiente de cobro)
```

#### 2.8 Alertas y Validaciones
```javascript
// Sistema de alertas visuales:
- ROJA: Producto controlado sin receta
- NARANJA: Paciente con alergias al principio activo
- AMARILLA: Producto próximo a vencer (< 3 meses)
- AZUL: Productos relacionados disponibles (cross-selling)
- VERDE: Descuento aplicable
```

### Vistas Backend

#### 2.9 Vista de Orden POS Farmacéutica
Extender vista de `pos.order` con:
- Sección de Información del Paciente
- Sección de Receta Asociada
- Desglose de Copagos y Seguros
- Botón "Generar Reclamación de Seguro"

### Reportes

#### 2.10 Ticket/Factura Farmacéutica
```xml
<!-- Incluir en el ticket:
- Datos del paciente
- Datos del prescriptor (si hay receta)
- Instrucciones de uso por producto
- Advertencias (efectos secundarios, contraindicaciones)
- Número de receta
- Fecha de dispensación
- Nombre del farmacéutico que dispensó
- Copago vs. cobertura de seguro
-->
```

### Modo Offline

#### 2.11 Gestión Offline
```python
# Para operación offline:
1. Caché local de:
   - Últimos 1000 pacientes activos
   - Información de seguros
   - Recetas activas (últimos 30 días)
   
2. Sincronización al reconectar:
   - Validar recetas con servidor
   - Obtener números de comprobante pendientes
   - Enviar reclamaciones de seguros pendientes
   
3. Lógica de números:
   - Usar secuencia local temporal: "TEMP-0001"
   - Al sincronizar, reemplazar con número definitivo del servidor
   - Mantener log de sincronización
```

### Entregable Fase 2

**Criterios de Aceptación:**
- [ ] POS identifica si es farmacia y adapta interfaz
- [ ] Selección de paciente obligatoria para medicamentos con receta
- [ ] Validación de recetas funcional
- [ ] Cálculo automático de copagos por plan de seguro
- [ ] Alertas visuales de alergias y contraindicaciones
- [ ] Productos relacionados se sugieren automáticamente
- [ ] Ticket incluye toda información farmacéutica requerida
- [ ] Modo offline funcional con sincronización posterior
- [ ] Tests de integración POS (mínimo 15 tests)

---

## FASE 3: SISTEMA DE COPAGO/SEGUROS (`pharmacy_insurance`)

### Objetivo
Sistema completo de gestión de copagos, reclamaciones a seguros y adjudicación de pagos.

### Modelos a Crear

#### 3.1 `pharmacy.insurance.plan`
Planes de seguro con configuraciones específicas:

```python
# Campos:
- name: Char (nombre del plan)
- insurance_company_id: Many2one a res.partner (aseguradora)
- plan_type: Selection ['hmo', 'ppo', 'pos', 'epo']
- tier_ids: One2many a pharmacy.insurance.tier (niveles de cobertura)
- formulary_ids: Many2many a product.template (medicamentos cubiertos)
- requires_prior_authorization: Boolean
- authorization_products: Many2many a product.template
- annual_deductible: Float
- out_of_pocket_max: Float
- copay_specialty: Float (copago para medicamentos especiales)
- active: Boolean

# Métodos:
- check_coverage(product_id): retorna si está cubierto y en qué tier
- calculate_patient_cost(product_id, price): calcula copago
- requires_authorization(product_id): verifica si requiere autorización previa
```

#### 3.2 `pharmacy.insurance.tier`
Niveles de cobertura (1, 2, 3):

```python
# Campos:
- plan_id: Many2one a pharmacy.insurance.plan
- tier_level: Selection ['1', '2', '3', '4']
- tier_name: Char ('Genéricos', 'Preferidos', 'No Preferidos', 'Especialidad')
- copay_type: Selection ['fixed', 'percentage']
- copay_amount: Float (cantidad fija)
- coinsurance_percentage: Float (porcentaje si es percentage)
- applies_to_deductible: Boolean
- product_ids: Many2many a product.template (productos en este tier)
```

#### 3.3 `pharmacy.insurance.claim`
Reclamaciones a seguros:

```python
# Campos:
- name: Char (número de reclamación, secuencia)
- claim_date: Datetime
- patient_id: Many2one a res.partner
- insurance_info_id: Many2one a pharmacy.insurance.info
- pos_order_id: Many2one a pos.order
- prescription_id: Many2one a pharmacy.prescription
- claim_line_ids: One2many a pharmacy.insurance.claim.line
- total_billed: Monetary (total facturado)
- total_approved: Monetary (total aprobado por seguro)
- total_rejected: Monetary (total rechazado)
- total_copay: Monetary (copago del paciente)
- state: Selection ['draft', 'submitted', 'processing', 'approved', 'partial', 'rejected', 'paid']
- submission_date: Datetime
- response_date: Datetime
- rejection_reason: Text
- approval_reference: Char
- payment_date: Date
- invoice_id: Many2one a account.move (factura al seguro)

# Métodos:
- action_submit(): envía reclamación (hoy simulado, luego con API)
- action_approve(): marca como aprobada
- action_reject(): marca como rechazada
- action_create_invoice(): crea factura al seguro
- _check_formulary_compliance(): verifica medicamentos cubiertos
```

#### 3.4 `pharmacy.insurance.claim.line`
Líneas de reclamación:

```python
# Campos:
- claim_id: Many2one a pharmacy.insurance.claim
- product_id: Many2one a product.template
- quantity: Float
- unit_price: Monetary
- total_amount: Monetary (quantity * unit_price)
- approved_amount: Monetary
- rejected_amount: Monetary
- copay_amount: Monetary
- rejection_reason: Text
- ndc_code: Char (código del medicamento)
- days_supply: Integer
- tier_level: Char
```

#### 3.5 `pharmacy.prior.authorization`
Autorizaciones previas:

```python
# Campos:
- name: Char (número de autorización)
- patient_id: Many2one a res.partner
- prescriber_id: Many2one a res.partner
- product_id: Many2one a product.template
- insurance_info_id: Many2one a pharmacy.insurance.info
- diagnosis_code: Char (ICD-10)
- justification: Text
- requested_date: Date
- authorization_date: Date
- expiration_date: Date
- authorization_number: Char
- quantity_authorized: Float
- state: Selection ['draft', 'requested', 'approved', 'denied', 'expired']
- denial_reason: Text

# Métodos:
- action_request(): solicita autorización
- action_approve(): aprueba manualmente
- action_deny(): deniega con motivo
- _check_expiration(): verifica vigencia
```

### Funcionalidad Adicional

#### 3.6 Dashboard de Reclamaciones
Crear vista kanban para seguimiento de reclamaciones:
- Estados: Borrador → Enviada → Procesando → Aprobada/Rechazada → Pagada
- Filtros por aseguradora, estado, fecha
- Gráficas de:
  - Tasa de aprobación por aseguradora
  - Monto promedio de copago
  - Tiempo promedio de adjudicación
  - Top 10 medicamentos más reclamados

#### 3.7 Integración con POS
```python
# Al confirmar venta en POS:
1. Si tiene seguro, crear automáticamente pharmacy.insurance.claim
2. Calcular copagos por línea según tier del plan
3. Generar dos pagos:
   - payment_method_id = Efectivo/Tarjeta (copago)
   - payment_method_id = Seguro Médico (monto a reclamar)
4. Marcar claim como 'draft' para revisión posterior
```

#### 3.8 Proceso de Adjudicación
```python
# Wizard: pharmacy.claim.adjudication.wizard
# Permite revisión masiva de claims:
- Seleccionar múltiples claims en estado 'submitted'
- Botón "Procesar Lote"
- Por cada claim:
  * Verificar cobertura de productos
  * Aplicar copagos según tier
  * Detectar productos que requieren autorización previa
  * Marcar estado según resultado
- Generar reporte de procesamiento
```

### Reportes

#### 3.9 Reporte de Reclamaciones
```xml
<!-- pharmacy_insurance_claim_report.xml
Incluye:
- Datos del paciente y seguro
- Detalle de productos reclamados
- Copagos vs. cobertura
- Estado de la reclamación
- Código de barras con número de reclamación
-->
```

#### 3.10 Análisis de Rentabilidad por Seguro
```python
# Reporte SQL personalizado:
SELECT 
    insurance_company.name,
    COUNT(claim.id) as total_claims,
    SUM(claim.total_billed) as total_billed,
    SUM(claim.total_approved) as total_approved,
    SUM(claim.total_rejected) as total_rejected,
    AVG(claim.total_copay) as avg_copay,
    (SUM(claim.total_approved) / SUM(claim.total_billed)) * 100 as approval_rate
FROM pharmacy_insurance_claim claim
JOIN pharmacy_insurance_info info ON claim.insurance_info_id = info.id
JOIN res_partner insurance_company ON info.insurance_company_id = insurance_company.id
GROUP BY insurance_company.name
```

### Entregable Fase 3

**Criterios de Aceptación:**
- [ ] Planes de seguro configurables con tiers
- [ ] Cálculo automático de copagos según tier del producto
- [ ] Reclamaciones se generan automáticamente desde POS
- [ ] Workflow completo de reclamación funcional
- [ ] Autorizaciones previas gestionables
- [ ] Dashboard de seguimiento operativo
- [ ] Reportes de reclamaciones imprimibles
- [ ] Análisis de rentabilidad por aseguradora
- [ ] Tests de lógica de negocio (mínimo 20 tests)

---

## FASE 4: GESTIÓN DE RECETAS MÉDICAS (`pharmacy_prescription`)

### Objetivo
Sistema completo de recepción, validación, dispensación y seguimiento de recetas médicas.

### Modelos a Crear

#### 4.1 `pharmacy.prescription`
Receta médica:

```python
# Campos:
- name: Char (número de receta, secuencia)
- prescription_date: Date
- reception_date: Date (fecha en que llega a farmacia)
- patient_id: Many2one a res.partner (domain: is_patient=True)
- prescriber_id: Many2one a res.partner (domain: is_prescriber=True)
- diagnosis: Char (diagnóstico)
- icd10_code: Char (código CIE-10)
- prescription_type: Selection ['paper', 'electronic', 'phone', 'fax']
- validity_days: Integer (default=30)
- expiration_date: Date (computed: prescription_date + validity_days)
- line_ids: One2many a pharmacy.prescription.line
- image: Binary (escaneo de receta en papel)
- state: Selection ['draft', 'received', 'validated', 'partially_dispensed', 'fully_dispensed', 'expired', 'cancelled']
- validation_state: Selection ['pending', 'approved', 'rejected']
- validated_by: Many2one a res.users (farmacéutico que validó)
- validation_date: Datetime
- validation_notes: Text
- rejection_reason: Text
- refills_allowed: Integer (número de resurtidos permitidos)
- refills_dispensed: Integer (computed)
- refills_remaining: Integer (computed)
- notes: Text (indicaciones especiales del médico)
- allergies_checked: Boolean (farmacéutico verificó alergias)
- interactions_checked: Boolean (farmacéutico verificó interacciones)
- dispensation_ids: One2many a pos.order (ventas que usaron esta receta)

# Constraints:
- _check_expiration: no permitir dispensar si está vencida
- _check_refills: no permitir más dispensaciones que refills_allowed

# Métodos:
- action_validate(): valida la receta (solo farmacéutico)
- action_reject(): rechaza con motivo
- _check_expiration(): verifica vigencia
- _check_interactions(): verifica interacciones medicamentosas
- _check_allergies(): verifica alergias del paciente
- action_dispense(): marca línea como dispensada
- _compute_refills(): calcula resurtidos restantes
```

#### 4.2 `pharmacy.prescription.line`
Líneas de la receta:

```python
# Campos:
- prescription_id: Many2one a pharmacy.prescription
- sequence: Integer
- product_id: Many2one a product.template (medicamento prescrito)
- generic_substitution_allowed: Boolean
- quantity_prescribed: Float
- quantity_dispensed: Float (acumulado)
- quantity_remaining: Float (computed)
- pharmaceutical_form: Selection (related de product_id)
- concentration: Char (related de product_id)
- dosage: Char (ej: "1 tableta cada 8 horas")
- duration_days: Integer (duración del tratamiento)
- administration_route: Selection ['oral', 'topica', 'intravenosa', 'intramuscular', 'subcutanea', 'oftalmica', 'otica', 'nasal', 'rectal', 'inhalatoria']
- frequency: Char (ej: "Cada 8 horas", "3 veces al día")
- special_instructions: Text
- state: Selection ['pending', 'partial', 'dispensed']
- dispensation_line_ids: One2many a pos.order.line

# Métodos:
- _compute_quantity_remaining(): calcula pendiente por dispensar
- can_dispense(quantity): valida si se puede dispensar cantidad
```

#### 4.3 `pharmacy.prescription.validation`
Log de validaciones:

```python
# Campos:
- prescription_id: Many2one a pharmacy.prescription
- validation_type: Selection ['dose', 'interaction', 'allergy', 'contraindication', 'expiration', 'duplication']
- severity: Selection ['info', 'warning', 'critical']
- message: Text
- detected_by: Many2one a res.users
- detection_date: Datetime
- action_taken: Text
- prescriber_contacted: Boolean
- resolution: Text
```

#### 4.4 `pharmacy.drug.interaction`
Base de datos de interacciones medicamentosas:

```python
# Campos:
- drug_a_id: Many2one a product.template
- drug_b_id: Many2one a product.template
- interaction_type: Selection ['major', 'moderate', 'minor']
- description: Text
- clinical_effects: Text
- recommendations: Text
- reference: Char (fuente de la información)

# Métodos:
- check_interaction(product_ids): retorna lista de interacciones detectadas
```

### Vistas

#### 4.5 Vista de Receta
```xml
<!-- Formulario con tabs:
1. Información General (paciente, prescriptor, diagnóstico)
2. Medicamentos Prescritos (tree con líneas)
3. Validación Farmacéutica (alertas, interacciones, alergias)
4. Historial de Dispensación (pos.orders relacionados)
5. Imagen de Receta (visor de PDF/imagen)
-->

<!-- Estados del workflow con botones:
- draft → received (botón "Recibir Receta")
- received → validated (botón "Validar" - solo farmacéutico)
- validated → dispensed (automático al vender en POS)
- received → rejected (botón "Rechazar")
-->
```

#### 4.6 Kanban de Recetas
```python
# Vista kanban agrupada por estado
# Tarjetas muestran:
- Foto del paciente
- Nombre del paciente
- Fecha de recepción
- Días para vencer
- Número de medicamentos
- Semáforo de prioridad
```

#### 4.7 Dashboard de Recetas
```xml
<!-- pharmacy_prescription_dashboard.xml
Incluye:
- Gráfico: Recetas recibidas vs. dispensadas (últimos 30 días)
- Gráfico: Tasa de validación vs. rechazo
- Gráfico: Tiempo promedio de procesamiento
- Lista: Recetas próximas a vencer (< 5 días)
- Lista: Recetas pendientes de validación
- Lista: Pacientes con recetas no retiradas
-->
```

### Wizard de Validación

#### 4.8 `pharmacy.prescription.validation.wizard`
```python
# Wizard para validación rápida:
# Campos:
- prescription_id: Many2one a pharmacy.prescription
- check_allergies: Boolean (default=True)
- check_interactions: Boolean (default=True)
- check_dosage: Boolean (default=True)
- check_contraindications: Boolean (default=True)
- validation_summary: Html (readonly, muestra resultados)
- has_critical_alerts: Boolean (computed)
- validation_notes: Text
- action: Selection ['approve', 'reject', 'contact_prescriber']

# Métodos:
- default_get(): ejecuta todas las validaciones automáticas
- action_validate(): aplica decisión del farmacéutico
- _check_all_validations(): ejecuta todas las verificaciones
```

### Integración con POS

#### 4.9 Flujo en POS
```javascript
// Al agregar producto con requires_prescription=True:
1. Verificar si cliente tiene recetas activas para ese producto
2. Si sí:
   - Mostrar recetas disponibles
   - Permitir seleccionar receta
   - Validar cantidad vs. cantidad restante en receta
   - Vincular línea de venta con línea de receta
3. Si no:
   - Mostrar modal "Crear Receta Rápida"
   - O "Continuar sin receta" (requiere justificación y autorización)
4. Al confirmar venta:
   - Actualizar quantity_dispensed en líneas de receta
   - Si quantity_remaining == 0, marcar línea como 'dispensed'
   - Si todas las líneas dispensed, marcar receta como 'fully_dispensed'
```

### Notificaciones y Recordatorios

#### 4.10 Sistema de Recordatorios
```python
# Cron job diario: pharmacy.prescription.reminder
# Envía notificaciones:
- Al paciente: "Su receta vence en 5 días"
- Al paciente: "Tiene medicamentos pendientes de retirar"
- A farmacia: "10 recetas próximas a vencer"
- Al paciente: "Es tiempo de resurtir su medicamento"

# Configuración en res.partner:
- send_refill_reminders: Boolean
- reminder_days_before: Integer (default=5)
- preferred_contact: Selection ['email', 'sms', 'whatsapp', 'phone']
```

### Reportes

#### 4.11 Receta Dispensada (Para el Paciente)
```xml
<!-- pharmacy_prescription_dispensation_report.xml
Incluye:
- Datos del paciente
- Datos del prescriptor
- Fecha de dispensación
- Medicamentos dispensados con:
  * Nombre comercial y genérico
  * Dosis y concentración
  * Cantidad dispensada
  * Instrucciones de uso (grande y legible)
  * Efectos secundarios comunes
  * Advertencias importantes
- Próxima fecha de resurtido
- Información de contacto de la farmacia
-->
```

### Entregable Fase 4

**Criterios de Aceptación:**
- [ ] Recetas capturables con todos sus campos
- [ ] Validación farmacéutica con detección de interacciones y alergias
- [ ] Workflow completo de receta funcional
- [ ] Integración con POS: vincular ventas a recetas
- [ ] Control de cantidades: no dispensar más de lo prescrito
- [ ] Control de resurtidos: máximo permitido
- [ ] Sistema de recordatorios funcional
- [ ] Dashboard operativo
- [ ] Reporte de dispensación para paciente
- [ ] Tests funcionales (mínimo 25 tests)

---

## FASE 5: SISTEMA DE DELIVERY (`pharmacy_delivery`)

### Objetivo
Gestionar pedidos a domicilio con seguimiento de estado y control de entregas.

### Modelos a Crear

#### 5.1 `pharmacy.delivery.order`
Orden de entrega:

```python
# Campos:
- name: Char (número de entrega, secuencia)
- order_date: Datetime
- sale_order_id: Many2one a sale.order
- pos_order_id: Many2one a pos.order
- prescription_id: Many2one a pharmacy.prescription
- patient_id: Many2one a res.partner
- delivery_address_id: Many2one a res.partner (dirección de entrega)
- delivery_address_text: Text (dirección completa en texto)
- phone: Char
- mobile: Char
- delivery_notes: Text (instrucciones de entrega)
- delivery_type: Selection ['standard', 'express', 'scheduled']
- scheduled_date: Datetime (para entregas programadas)
- delivery_time_window: Selection ['morning', 'afternoon', 'evening', 'anytime']
- courier_id: Many2one a res.users (repartidor asignado)
- state: Selection ['draft', 'confirmed', 'ready', 'assigned', 'in_transit', 'delivered', 'failed', 'cancelled']
- prepared_by: Many2one a res.users
- preparation_date: Datetime
- dispatch_date: Datetime
- delivery_date: Datetime
- failed_reason: Text
- failed_attempts: Integer
- line_ids: One2many a pharmacy.delivery.order.line
- total_amount: Monetary
- payment_method: Selection ['prepaid', 'cash_on_delivery', 'card_on_delivery']
- payment_state: Selection ['pending', 'paid']
- requires_signature: Boolean
- signature: Binary
- photo_proof: Binary (foto de entrega)
- delivery_rating: Selection ['1', '2', '3', '4', '5']
- customer_feedback: Text

# Métodos:
- action_confirm(): confirma el pedido
- action_prepare(): marca como listo para despacho
- action_assign_courier(): asigna repartidor
- action_dispatch(): marca como en tránsito
- action_deliver(): completa entrega
- action_fail(): marca como fallida
- _send_notification(state): envía notificación al cliente por estado
```

#### 5.2 `pharmacy.delivery.order.line`
Líneas de entrega:

```python
# Campos:
- delivery_order_id: Many2one a pharmacy.delivery.order
- product_id: Many2one a product.template
- quantity: Float
- price_unit: Monetary
- price_subtotal: Monetary
- lot_id: Many2one a stock.lot
- special_instructions: Text (ej: "Mantener refrigerado")
```

#### 5.3 `pharmacy.delivery.zone`
Zonas de entrega:

```python
# Campos:
- name: Char (nombre de la zona)
- zip_codes: Text (códigos postales separados por coma)
- polygon_coords: Text (coordenadas del polígono geográfico, opcional)
- delivery_cost: Monetary
- delivery_time_standard: Integer (minutos)
- delivery_time_express: Integer (minutos)
- active: Boolean
- available_time_slots: One2many a pharmacy.delivery.time.slot
```

#### 5.4 `pharmacy.delivery.time.slot`
Horarios disponibles:

```python
# Campos:
- zone_id: Many2one a pharmacy.delivery.zone
- day_of_week: Selection ['0', '1', '2', '3', '4', '5', '6']
- time_from: Float (hora en formato 24h)
- time_to: Float
- max_deliveries: Integer (capacidad máxima)
- active: Boolean
```

#### 5.5 `pharmacy.delivery.route`
Rutas de entrega:

```python
# Campos:
- name: Char (nombre de ruta, ej: "Ruta Matutina Norte")
- route_date: Date
- courier_id: Many2one a res.users
- delivery_ids: Many2many a pharmacy.delivery.order
- state: Selection ['draft', 'in_progress', 'completed']
- start_time: Datetime
- end_time: Datetime
- total_deliveries: Integer (computed)
- successful_deliveries: Integer (computed)
- failed_deliveries: Integer (computed)

# Métodos:
- action_optimize_route(): ordena entregas por proximidad geográfica
- action_start(): inicia la ruta
- action_complete(): finaliza la ruta
```

### Vistas

#### 5.6 Vista de Orden de Entrega
```xml
<!-- Formulario con secciones:
1. Información del Cliente (paciente, dirección, teléfono)
2. Detalles del Pedido (productos, receta asociada)
3. Información de Entrega (tipo, fecha programada, repartidor)
4. Seguimiento (estados, fechas, intentos)
5. Confirmación (firma, foto, rating)
-->

<!-- Workflow con botones de estado:
draft → confirmed → ready → assigned → in_transit → delivered
                                                   ↘ failed
-->
```

#### 5.7 Kanban de Entregas
```python
# Vista kanban agrupada por estado
# Colores:
- draft: gris
- confirmed: azul
- ready: amarillo
- assigned: naranja
- in_transit: verde
- delivered: verde oscuro
- failed: rojo

# Cada tarjeta muestra:
- Nombre del paciente
- Dirección (resumida)
- Productos (cantidad)
- Repartidor asignado
- Tiempo estimado de entrega
- Botón rápido de cambio de estado
```

#### 5.8 Mapa de Entregas (opcional para futuro)
```xml
<!-- Vista de mapa con:
- Ubicación de la farmacia (central)
- Pins de entregas pendientes (coloreados por estado)
- Rutas óptimas sugeridas
- Posición actual del repartidor (futuro con GPS)
-->
```

#### 5.9 Dashboard de Delivery
```xml
<!-- pharmacy_delivery_dashboard.xml
Incluye:
- KPI: Entregas del día (pendientes / completadas / fallidas)
- KPI: Tiempo promedio de entrega
- KPI: Tasa de éxito de entregas
- Gráfico: Entregas por hora del día
- Gráfico: Entregas por zona
- Lista: Entregas en tránsito (con tiempo transcurrido)
- Lista: Entregas atrasadas
- Lista: Repartidores disponibles
-->
```

### Portal del Cliente

#### 5.10 Vista Portal para Seguimiento
```python
# Extender portal.mixin en pharmacy.delivery.order
# Permitir al cliente:
- Ver estado de su entrega en tiempo real
- Ver productos incluidos
- Fecha estimada de entrega
- Nombre del repartidor (cuando esté asignado)
- Botón "Contactar Farmacia"
- Dejar rating y comentarios (post-entrega)

# URL: /my/delivery/XXXX
```

### Integración con POS

#### 5.11 Creación de Entrega desde POS
```javascript
// En PaymentScreen, agregar botón "Entrega a Domicilio"
// Al hacer clic:
1. Mostrar modal de datos de entrega
2. Campos:
   - Dirección (autocompletar de partner_id)
   - Teléfono
   - Tipo de entrega (standard/express)
   - Fecha programada (si aplica)
   - Notas especiales
3. Calcular costo de envío según zona
4. Agregar línea de "Servicio de Delivery" al pedido
5. Al confirmar venta:
   - Crear automáticamente pharmacy.delivery.order
   - Estado inicial: 'draft'
   - Vincular a pos.order
```

### Integración con Sale Order

#### 5.12 Pedidos Web
```python
# Si tienes eCommerce de Odoo:
# Al confirmar sale.order con delivery=True:
1. Validar que productos requieran receta
2. Si requieren receta:
   - Solicitar carga de imagen de receta
   - Crear pharmacy.prescription en estado 'received'
   - Bloquear entrega hasta validación de farmacéutico
3. Crear pharmacy.delivery.order
4. Notificar a farmacia de nuevo pedido
```

### Notificaciones

#### 5.13 Sistema de Notificaciones Automáticas
```python
# Por cada cambio de estado, enviar notificación al cliente:
- confirmed: "Su pedido ha sido confirmado. Estamos preparando sus medicamentos."
- ready: "Su pedido está listo para despacho."
- assigned: "Su pedido fue asignado a [Repartidor]. Entrega estimada: [Hora]."
- in_transit: "Su pedido está en camino. Llegada estimada en [X] minutos."
- delivered: "Su pedido ha sido entregado. ¡Gracias por su compra!"
- failed: "No pudimos entregar su pedido. Motivo: [Razón]. Contacte a la farmacia."

# Métodos de notificación:
- Email (siempre)
- SMS (si está configurado)
- WhatsApp (si está configurado, usar API)
- Notificación push (si hay app móvil)
```

### Gestión de Repartidores

#### 5.14 `res.users` (Extensión)
```python
# Campos adicionales:
- is_delivery_courier: Boolean
- courier_active: Boolean (disponible para asignación)
- vehicle_type: Selection ['bike', 'motorcycle', 'car', 'van']
- vehicle_plate: Char
- max_deliveries_per_route: Integer
- delivery_zone_ids: Many2many a pharmacy.delivery.zone
- current_route_id: Many2one a pharmacy.delivery.route
- total_deliveries: Integer (computed, histórico)
- average_delivery_time: Float (computed, en minutos)
- success_rate: Float (computed, porcentaje)
```

### Reportes

#### 5.15 Hoja de Ruta para Repartidor
```xml
<!-- pharmacy_delivery_route_report.xml
Imprimir lista de entregas del día con:
- Número de orden
- Nombre del cliente
- Dirección completa
- Teléfono
- Productos a entregar
- Monto a cobrar (si es contra entrega)
- Casilla para firma del cliente
- Ordenado por optimización de ruta
-->
```

#### 5.16 Reporte de Desempeño de Delivery
```python
# Reporte mensual con:
- Total de entregas realizadas
- Tasa de éxito vs. fallas
- Tiempo promedio de entrega
- Entregas por repartidor
- Zonas con más demanda
- Horarios pico
- Rating promedio de clientes
```

### Entregable Fase 5

**Criterios de Aceptación:**
- [ ] Órdenes de delivery creables desde POS y Sale Order
- [ ] Workflow completo de estados funcional
- [ ] Asignación de repartidores funcional
- [ ] Zonas de entrega configurables con costos
- [ ] Cálculo automático de costo de envío
- [ ] Notificaciones automáticas por cambio de estado
- [ ] Portal de seguimiento para clientes
- [ ] Dashboard de operación de delivery
- [ ] Rutas optimizables (orden sugerido de entregas)
- [ ] Hoja de ruta imprimible
- [ ] Tests de integración (mínimo 20 tests)

---

## FASE 6: MEJORAS DE INVENTARIO FARMACÉUTICO (`pharmacy_stock_enhanced`)

### Objetivo
Extender el módulo stock de Odoo con funcionalidades específicas para control farmacéutico: lotes, caducidades, alertas, FEFO, y trazabilidad.

### Modelos a Extender

#### 6.1 `stock.lot` (Extensión)
```python
# Campos adicionales:
- is_pharmaceutical: Boolean (related de product_id)
- expiration_date: Date (ya existe en Odoo, asegurar uso obligatorio)
- expiration_alert_date: Date (computed: expiration_date - alert_days)
- alert_days_before: Integer (default=90, configurable por producto)
- expiration_state: Selection [
    ('good', 'Bueno (>6 meses)'),
    ('warning', 'Precaución (3-6 meses)'),
    ('critical', 'Crítico (<3 meses)'),
    ('expired', 'Vencido')
] (computed)
- quarantine: Boolean (lote en cuarentena, no vendible)
- quarantine_reason: Text
- quality_control_passed: Boolean
- quality_control_date: Date
- quality_control_by: Many2one a res.users
- temperature_controlled: Boolean
- min_temperature: Float
- max_temperature: Float
- temperature_log_ids: One2many a pharmacy.temperature.log
- origin_country: Char
- import_permit: Char
- sanitary_registration: Char

# Constraints:
- _check_expiration_date: fecha de caducidad obligatoria si is_pharmaceutical
- _check_not_expired: no permitir movimientos de lotes vencidos

# Métodos:
- _compute_expiration_state(): actualiza estado según fecha
- action_quarantine(): pone lote en cuarentena
- action_release_quarantine(): libera lote
- _cron_check_expirations(): cron diario que verifica vencimientos
```

#### 6.2 `pharmacy.temperature.log`
Registro de temperatura (para productos refrigerados):

```python
# Campos:
- lot_id: Many2one a stock.lot
- date: Datetime
- temperature: Float
- humidity: Float (opcional)
- in_range: Boolean (computed)
- recorded_by: Many2one a res.users
- location_id: Many2one a stock.location
- notes: Text

# Métodos:
- _check_temperature_range(): valida si está en rango permitido
```

#### 6.3 `product.template` (Extensión adicional)
```python
# Campos nuevos para control de inventario:
- use_expiration_date: Boolean (forzar a True si is_pharmaceutical)
- expiration_alert_days: Integer (días antes de vencer para alertar)
- minimum_shelf_life_days: Integer (vida útil mínima aceptable al recibir)
- rotation_method: Selection ['fefo', 'fifo', 'lifo'] (default='fefo' para farmacia)
- automatic_lot_assignment: Boolean (asignar lote automáticamente en ventas)
- preferred_lot_selection: Selection [
    ('nearest_expiry', 'Próximo a Vencer (FEFO)'),
    ('farthest_expiry', 'Más Lejano'),
    ('largest_quantity', 'Mayor Cantidad'),
    ('manual', 'Selección Manual')
]
- storage_conditions: Text (condiciones de almacenamiento)
- requires_cold_chain: Boolean
```

#### 6.4 `stock.picking` (Extensión)
```python
# Campos adicionales:
- has_expiring_products: Boolean (computed, alerta visual)
- has_expired_products: Boolean (computed, bloquear si True)
- requires_cold_chain: Boolean (computed, si algún producto lo requiere)
- quality_check_required: Boolean
- quality_check_passed: Boolean
- quality_checked_by: Many2one a res.users
- quality_check_date: Datetime
- temperature_at_reception: Float (para recepciones)

# Métodos:
- _check_expiration_dates(): valida fechas de caducidad antes de confirmar
- action_quality_check(): wizard de control de calidad
```

#### 6.5 `stock.move.line` (Extensión)
```python
# Campos adicionales:
- expiration_date: Date (related de lot_id, para vista rápida)
- days_to_expiry: Integer (computed)
- expiration_status: Selection (related de lot_id)
- lot_assignment_method: Selection (indica cómo se asignó el lote)

# Métodos:
- _auto_assign_lot(): asigna lote automáticamente según FEFO u otro método
```

### Nuevos Modelos

#### 6.6 `pharmacy.stock.alert`
Alertas de inventario:

```python
# Campos:
- name: Char (descripción de la alerta)
- alert_type: Selection [
    ('expiration', 'Próximo a Vencer'),
    ('expired', 'Vencido'),
    ('low_stock', 'Stock Bajo'),
    ('no_stock', 'Sin Stock'),
    ('quarantine', 'Producto en Cuarentena'),
    ('temperature', 'Temperatura Fuera de Rango')
]
- severity: Selection ['low', 'medium', 'high', 'critical']
- product_id: Many2one a product.template
- lot_id: Many2one a stock.lot
- location_id: Many2one a stock.location
- alert_date: Datetime
- expiration_date: Date (si alert_type='expiration')
- quantity_available: Float
- resolved: Boolean
- resolved_date: Datetime
- resolved_by: Many2one a res.users
- action_taken: Text

# Métodos:
- action_resolve(): marca como resuelta
- _cron_generate_alerts(): cron que genera alertas diarias
```

#### 6.7 `pharmacy.stock.adjustment`
Ajustes de inventario (vencimientos, daños, etc.):

```python
# Campos:
- name: Char (número de ajuste)
- adjustment_date: Date
- adjustment_type: Selection [
    ('expiration', 'Vencimiento'),
    ('damage', 'Producto Dañado'),
    ('theft', 'Robo/Pérdida'),
    ('quality', 'Rechazo de Calidad'),
    ('return', 'Devolución'),
    ('other', 'Otro')
]
- product_id: Many2one a product.template
- lot_id: Many2one a stock.lot
- quantity: Float
- cost: Monetary (computed: quantity * standard_price)
- reason: Text
- approved_by: Many2one a res.users
- state: Selection ['draft', 'approved', 'done']
- stock_move_id: Many2one a stock.move (movimiento generado)

# Métodos:
- action_approve(): aprueba el ajuste (solo manager)
- action_process(): ejecuta el movimiento de inventario
```

### Funcionalidades

#### 6.8 Asignación Automática de Lotes (FEFO)
```python
# Al confirmar picking de salida:
# Método en stock.move: _action_assign_lots_fefo()

def _action_assign_lots_fefo(self):
    """
    Asigna lotes automáticamente usando FEFO
    (First Expired, First Out - Primero que vence, primero que sale)
    """
    for move in self:
        if not move.product_id.is_pharmaceutical:
            continue
            
        # Buscar lotes disponibles del producto
        available_lots = self.env['stock.quant'].search([
            ('product_id', '=', move.product_id.id),
            ('location_id', '=', move.location_id.id),
            ('quantity', '>', 0),
            ('lot_id', '!=', False),
            ('lot_id.quarantine', '=', False),
            ('lot_id.expiration_state', '!=', 'expired')
        ])
        
        # Ordenar por fecha de vencimiento (FEFO)
        available_lots = available_lots.sorted(
            lambda q: q.lot_id.expiration_date
        )
        
        # Asignar cantidad requerida desde los lotes
        remaining_qty = move.product_uom_qty
        for quant in available_lots:
            if remaining_qty <= 0:
                break
                
            qty_from_lot = min(quant.quantity, remaining_qty)
            
            # Crear move line
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'lot_id': quant.lot_id.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'product_uom_qty': 0,  # Odoo 18 usa qty_done
                'qty_done': qty_from_lot,
                'product_uom_id': move.product_uom.id,
                'lot_assignment_method': 'fefo_auto'
            })
            
            remaining_qty -= qty_from_lot
```

#### 6.9 Wizard de Control de Calidad
```python
# pharmacy.quality.check.wizard

class PharmacyQualityCheckWizard(models.TransientModel):
    _name = 'pharmacy.quality.check.wizard'
    
    picking_id = fields.Many2one('stock.picking')
    line_ids = fields.One2many('pharmacy.quality.check.line', 'wizard_id')
    all_passed = fields.Boolean(compute='_compute_all_passed')
    notes = fields.Text()
    
    def action_approve(self):
        # Marcar picking como quality_check_passed=True
        # Crear lotes si no existen
        # Confirmar picking
        pass
    
    def action_reject(self):
        # Poner productos en cuarentena
        # Crear ajuste de inventario
        # Notificar a compras
        pass

class PharmacyQualityCheckLine(models.TransientModel):
    _name = 'pharmacy.quality.check.line'
    
    wizard_id = fields.Many2one('pharmacy.quality.check.wizard')
    move_line_id = fields.Many2one('stock.move.line')
    product_id = fields.Many2one('product.template')
    lot_id = fields.Many2one('stock.lot')
    quantity = fields.Float()
    expiration_date = fields.Date()
    packaging_ok = fields.Boolean()
    labeling_ok = fields.Boolean()
    temperature_ok = fields.Boolean()
    passed = fields.Boolean(compute='_compute_passed')
    rejection_reason = fields.Text()
```

### Cron Jobs

#### 6.10 `pharmacy_stock_expiration_alert`
```python
# Ejecutar diariamente a las 6:00 AM
# Busca:
1. Lotes próximos a vencer (< 90 días) → crear alerta 'medium'
2. Lotes próximos a vencer (< 30 días) → crear alerta 'high'
3. Lotes vencidos → crear alerta 'critical'
4. Productos con stock bajo → crear alerta 'low_stock'
5. Productos sin stock → crear alerta 'no_stock'

# Enviar resumen por email a:
- Gerente de farmacia
- Encargado de compras
```

#### 6.11 `pharmacy_stock_quarantine_expired`
```python
# Ejecutar diariamente a las 7:00 AM
# Busca lotes vencidos y automáticamente:
1. Poner en cuarentena (quarantine=True)
2. Crear ajuste de inventario tipo 'expiration'
3. Generar reporte de pérdidas
4. Notificar a gerencia
```

### Vistas

#### 6.12 Vista de Lote Farmacéutico
```xml
<!-- Extender vista de stock.lot con:
- Semáforo de estado de vencimiento (verde/amarillo/rojo)
- Sección de control de calidad
- Sección de temperatura (si aplica)
- Botones: "Cuarentena" / "Liberar" / "Dar de Baja"
- Gráfico de temperatura en el tiempo
-->
```

#### 6.13 Dashboard de Inventario Farmacéutico
```xml
<!-- pharmacy_stock_dashboard.xml
Incluye:
- KPI: Productos próximos a vencer (< 90 días)
- KPI: Productos vencidos (valor monetario)
- KPI: Productos en cuarentena
- KPI: Alertas activas por severidad
- Gráfico: Vencimientos por mes (próximos 12 meses)
- Gráfico: Valor de inventario por categoría ABC
- Lista: Top 10 productos próximos a vencer
- Lista: Productos con stock bajo
- Lista: Alertas sin resolver
-->
```

#### 6.14 Vista Kanban de Alertas
```python
# Agrupado por alert_type
# Colores por severity:
- low: verde
- medium: amarillo
- high: naranja
- critical: rojo

# Botones rápidos:
- "Resolver"
- "Ver Producto"
- "Crear Ajuste"
```

### Reportes

#### 6.15 Reporte de Vencimientos
```xml
<!-- pharmacy_expiration_report.xml
Filtrable por:
- Rango de fechas de vencimiento
- Categoría de producto
- Ubicación
- Estado (próximo / vencido)

Incluye:
- Producto
- Lote
- Fecha de vencimiento
- Días restantes
- Cantidad disponible
- Valor monetario
- Acciones sugeridas
-->
```

#### 6.16 Reporte de Pérdidas por Vencimiento
```python
# Mensual/Anual
# Incluye:
- Total de unidades dadas de baja
- Valor monetario total de pérdidas
- Pérdidas por categoría de producto
- Comparativo mes a mes
- Productos con mayor pérdida
- Análisis de causas
- Recomendaciones de mejora
```

### Integraciones

#### 6.17 Integración con POS
```python
# Al vender en POS:
1. Verificar expiration_state del lote
2. Si state='warning': mostrar alerta "Producto próximo a vencer"
3. Si state='critical': mostrar alerta roja "Producto vence en X días"
4. Si state='expired': bloquear venta, mostrar error
5. Asignar automáticamente lote según FEFO
6. Actualizar quantity_dispensed si está vinculado a receta
```

#### 6.18 Integración con Compras
```python
# Al recibir productos:
1. Wizard de control de calidad obligatorio
2. Validar minimum_shelf_life_days
3. Si expiration_date < today + minimum_shelf_life_days:
   - Rechazar recepción
   - Notificar a proveedor
   - Crear reclamo
4. Registrar temperatura de recepción
5. Si temperature_controlled y fuera de rango:
   - Poner en cuarentena automáticamente
```

### Entregable Fase 6

**Criterios de Aceptación:**
- [ ] Lotes con control de caducidad obligatorio
- [ ] Estados de vencimiento automáticos (bueno/precaución/crítico/vencido)
- [ ] Sistema FEFO funcional en ventas
- [ ] Alertas automáticas de vencimientos
- [ ] Wizard de control de calidad en recepciones
- [ ] Sistema de cuarentena funcional
- [ ] Registro de temperatura para productos refrigerados
- [ ] Dashboard de inventario farmacéutico
- [ ] Cron jobs de alertas y cuarentena operativos
- [ ] Reporte de vencimientos
- [ ] Reporte de pérdidas por vencimiento
- [ ] Integración con POS (bloqueo de vencidos, FEFO)
- [ ] Tests de lógica de inventario (mínimo 25 tests)

---

## INSTRUCCIONES GENERALES DE DESARROLLO

### Estándares de Código

1. **Nomenclatura:**
   - Modelos: `pharmacy.nombre_modelo` (snake_case)
   - Clases Python: `PharmacyNombreModelo` (PascalCase)
   - Campos: `nombre_campo` (snake_case)
   - Métodos: `_metodo_privado`, `metodo_publico` (snake_case)
   - Vistas XML: `pharmacy_modelo_vista_tipo` (snake_case)

2. **Estructura de Carpetas:**
```
pharmacy_modulo/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── modelo1.py
│   ├── modelo2.py
├── views/
│   ├── modelo1_views.xml
│   ├── modelo2_views.xml
│   ├── menus.xml
├── security/
│   ├── ir.model.access.csv
│   ├── security.xml
├── data/
│   ├── sequences.xml
│   ├── data.xml
├── demo/
│   ├── demo.xml
├── wizards/
│   ├── __init__.py
│   ├── wizard1.py
├── reports/
│   ├── __init__.py
│   ├── report_templates.xml
│   ├── report1.py
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   ├── index.html
│   ├── src/
│   │   ├── js/
│   │   ├── xml/
│   │   ├── scss/
├── tests/
│   ├── __init__.py
│   ├── test_modelo1.py
│   ├── test_modelo2.py
└── README.md
```

3. **Documentación:**
   - Docstrings en todos los modelos, métodos y funciones
   - Comentarios en lógica compleja
   - README.md con instrucciones de instalación y uso

4. **Seguridad:**
   - Definir grupos de acceso claros
   - Usar `ir.model.access.csv` para permisos de modelo
   - Usar `<record>` de seguridad para reglas de registro
   - Validar permisos en métodos sensibles

### Versionado y Git

```
# Commits descriptivos:
- [ADD] pharmacy_base: modelos base de farmacia
- [IMP] pharmacy_pos: mejora en cálculo de copagos
- [FIX] pharmacy_prescription: corrección en validación de recetas
- [REF] pharmacy_stock_enhanced: refactorización de asignación FEFO
```

### Testing

- **Coverage mínimo:** 70% por módulo
- **Tipos de tests:**
  - Unit tests: lógica de negocio de modelos
  - Integration tests: flujos completos (crear receta → vender en POS → delivery)
  - UI tests: validación de vistas y wizards

### Performance

- Usar `@api.depends` correctamente en campos computed
- Evitar búsquedas dentro de loops
- Usar `search_count()` en lugar de `len(search())`
- Indexar campos de búsqueda frecuente
- Usar `_sql_constraints` para validaciones en base de datos

### Internacionalización

- Todos los strings visibles deben ser traducibles
- Usar `_("String")` en Python
- Usar `<field name="string">` en XML con `t-translation="off"` cuando sea necesario
- Proveer archivos `.pot` y `.po` para español e inglés

---

## PLAN DE ENTREGA

### Sprint 1: Fundamentos (Semana 1-2)
- **Entregable:** `pharmacy_base` + `pharmacy_pos` (funcionalidades básicas)
- **Validación:** Venta de medicamentos OTC sin receta

### Sprint 2: Seguros y Recetas (Semana 3-4)
- **Entregable:** `pharmacy_insurance` + `pharmacy_prescription`
- **Validación:** Venta de medicamento con receta y aplicación de copago

### Sprint 3: Delivery (Semana 5)
- **Entregable:** `pharmacy_delivery`
- **Validación:** Pedido a domicilio desde POS hasta entrega

### Sprint 4: Inventario Avanzado (Semana 6)
- **Entregable:** `pharmacy_stock_enhanced`
- **Validación:** Recepción con control de calidad, FEFO en ventas, alertas de vencimiento

### Sprint 5: Refinamiento y Testing (Semana 7)
- Tests completos de todos los módulos
- Corrección de bugs
- Optimización de performance
- Documentación final

---

## CRITERIOS DE ACEPTACIÓN GLOBALES

1. **Funcionalidad:**
   - [ ] Todos los flujos descritos funcionan sin errores
   - [ ] Validaciones de negocio implementadas correctamente
   - [ ] Cálculos precisos (copagos, vencimientos, cantidades)

2. **Usabilidad:**
   - [ ] Interfaz intuitiva para usuarios no técnicos
   - [ ] Mensajes de error claros y accionables
   - [ ] Wizards guían al usuario en procesos complejos

3. **Performance:**
   - [ ] POS responde en < 2 segundos
   - [ ] Búsquedas de productos < 1 segundo
   - [ ] Generación de reportes < 5 segundos

4. **Escalabilidad:**
   - [ ] Soporta 10,000 transacciones diarias
   - [ ] Funciona con 50+ sucursales
   - [ ] Base de datos de 100,000+ productos

5. **Seguridad:**
   - [ ] Datos de pacientes protegidos
   - [ ] Accesos controlados por roles
   - [ ] Logs de auditoría en operaciones sensibles

6. **Mantenibilidad:**
   - [ ] Código limpio y documentado
   - [ ] Tests con 70%+ coverage
   - [ ] Documentación técnica completa

---

## NOTAS IMPORTANTES

1. **Prioriza la funcionalidad core sobre features avanzadas**
2. **Cada entregable debe ser desplegable en producción**
3. **Mantén la compatibilidad con módulos estándar de Odoo**
4. **Piensa en la escalabilidad desde el inicio**
5. **La experiencia del usuario es clave en POS**
6. **Seguridad de datos médicos es CRÍTICA**

---

## PREGUNTAS ANTES DE COMENZAR

Antes de iniciar el desarrollo, confirma:

1. ¿Versión exacta de Odoo? (18.0, 18.1, etc.)
2. ¿Base de datos de prueba disponible?
3. ¿Entorno de desarrollo configurado?
4. ¿Acceso a repositorio Git?
5. ¿Stakeholders definidos para validaciones?

---

**¡Comienza con la Fase 1 (`pharmacy_base`) y avanza incrementalmente!**