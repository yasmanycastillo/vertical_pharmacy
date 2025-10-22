# ESPECIFICACIONES TÉCNICAS - MÓDULOS FARMACIA ODOO 18

## MODO OFFLINE EN POS

### Problemática
El POS debe funcionar sin conexión a internet, pero algunos procesos requieren:
- Números de comprobante fiscales (secuencias del servidor)
- Validación de recetas con el servidor
- Envío de claims a seguros

### Solución Implementada

#### 1. Caché Local en POS

```javascript
// Datos que se cargan al iniciar sesión POS
const offlineData = {
    // Últimos 1000 pacientes activos
    patients: [],
    
    // Información de seguros de pacientes cargados
    insurance_info: [],
    
    // Recetas activas (últimos 30 días)
    prescriptions: [],
    
    // Productos con stock disponible
    products: [],
    
    // Lotes con vencimientos
    lots: [],
    
    // Últimas 100 transacciones del día
    orders: []
};
```

#### 2. Numeración Temporal

```python
# En pos.order (Python)
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # Si está offline (detectado por falta de session_id actualizado)
        if self._is_offline_mode():
            # Usar numeración temporal
            vals['name'] = f"TEMP-{self.env.company.id}-{int(time.time())}"
            vals['needs_sync'] = True
        else:
            # Numeración normal del servidor
            vals['name'] = self.env['ir.sequence'].next_by_code('pos.order')
    
    return super().create(vals_list)

def _sync_offline_orders(self):
    """Sincroniza órdenes creadas offline"""
    offline_orders = self.search([('needs_sync', '=', True)])
    
    for order in offline_orders:
        # Obtener número definitivo
        definitive_number = self.env['ir.sequence'].next_by_code('pos.order')
        
        # Actualizar orden
        order.write({
            'name': definitive_number,
            'needs_sync': False,
            'synced_at': fields.Datetime.now()
        })
        
        # Log de sincronización
        self.env['pharmacy.sync.log'].create({
            'order_id': order.id,
            'temp_number': order.name,
            'definitive_number': definitive_number,
            'sync_date': fields.Datetime.now()
        })
```

#### 3. Validación Diferida de Recetas

```javascript
// En POS (JavaScript)
async validatePrescription(prescriptionId, offline = false) {
    if (offline) {
        // Validación básica local
        const prescription = this.offlineData.prescriptions.find(
            p => p.id === prescriptionId
        );
        
        if (!prescription) {
            return {
                valid: false,
                reason: 'Receta no encontrada en caché local'
            };
        }
        
        // Verificar expiración
        if (new Date(prescription.expiration_date) < new Date()) {
            return {
                valid: false,
                reason: 'Receta vencida'
            };
        }
        
        // Marcar para validación posterior
        this.pendingValidations.push({
            prescription_id: prescriptionId,
            validated_at: new Date(),
            needs_server_validation: true
        });
        
        return {
            valid: true,
            reason: 'Validación local OK - Requiere confirmación online',
            pending: true
        };
    } else {
        // Validación completa en servidor
        return await this.rpc({
            model: 'pharmacy.prescription',
            method: 'validate_prescription',
            args: [prescriptionId]
        });
    }
}
```

#### 4. Claims de Seguro en Cola

```python
# Modelo para cola de sincronización
class PharmacyInsuranceClaimQueue(models.Model):
    _name = 'pharmacy.insurance.claim.queue'
    _description = 'Cola de Claims Pendientes de Envío'
    
    pos_order_id = fields.Many2one('pos.order', required=True)
    insurance_info_id = fields.Many2one('pharmacy.insurance.info', required=True)
    claim_data = fields.Json('Datos del Claim')
    created_offline = fields.Boolean(default=False)
    synced = fields.Boolean(default=False)
    sync_attempts = fields.Integer(default=0)
    last_sync_attempt = fields.Datetime()
    error_message = fields.Text()
    
    def _cron_process_claim_queue(self):
        """Cron que procesa claims pendientes cada 15 minutos"""
        pending_claims = self.search([
            ('synced', '=', False),
            ('sync_attempts', '<', 5)
        ], limit=100)
        
        for queue_item in pending_claims:
            try:
                # Crear claim real
                claim = self.env['pharmacy.insurance.claim'].create(
                    queue_item.claim_data
                )
                
                # Marcar como sincronizado
                queue_item.write({
                    'synced': True,
                    'last_sync_attempt': fields.Datetime.now()
                })
                
            except Exception as e:
                queue_item.write({
                    'sync_attempts': queue_item.sync_attempts + 1,
                    'last_sync_attempt': fields.Datetime.now(),
                    'error_message': str(e)
                })
```

#### 5. Sincronización Automática

```javascript
// En POS (JavaScript)
class PharmacyPOS extends POS {
    async afterProcessOrder(order) {
        const result = await super.afterProcessOrder(order);
        
        // Intentar sincronizar si hay conexión
        if (this.isOnline()) {
            await this.syncPendingData();
        }
        
        return result;
    }
    
    async syncPendingData() {
        try {
            // 1. Sincronizar órdenes con numeración temporal
            await this.rpc({
                model: 'pos.order',
                method: '_sync_offline_orders',
                args: []
            });
            
            // 2. Validar recetas pendientes
            for (const validation of this.pendingValidations) {
                await this.rpc({
                    model: 'pharmacy.prescription',
                    method: 'validate_prescription_deferred',
                    args: [validation.prescription_id]
                });
            }
            this.pendingValidations = [];
            
            // 3. Procesar claims en cola
            await this.rpc({
                model: 'pharmacy.insurance.claim.queue',
                method: '_cron_process_claim_queue',
                args: []
            });
            
            // Notificar al usuario
            this.showNotification('Sincronización completada', {
                type: 'success'
            });
            
        } catch (error) {
            console.error('Error en sincronización:', error);
            // No bloquear operación, reintentar después
        }
    }
}
```

---

## PERFORMANCE Y ESCALABILIDAD

### Targets de Performance

| Operación | Target | Crítico |
|-----------|--------|---------|
| Carga inicial POS | < 5 seg | < 10 seg |
| Agregar producto a orden | < 500ms | < 1 seg |
| Búsqueda de producto | < 300ms | < 1 seg |
| Búsqueda de paciente | < 500ms | < 1 seg |
| Cálculo de copago | < 200ms | < 500ms |
| Validación de receta | < 1 seg | < 3 seg |
| Confirmar orden | < 1 seg | < 2 seg |
| Generar ticket | < 500ms | < 1 seg |

### Optimizaciones Implementadas

#### 1. Índices en Base de Datos

```python
# En modelos críticos
class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    
    # Campos con búsquedas frecuentes deben tener index=True
    name = fields.Char(index=True)  # Número de receta
    patient_id = fields.Many2one('res.partner', index=True)
    prescription_date = fields.Date(index=True)
    state = fields.Selection(index=True)
    
    # Índice compuesto para búsquedas complejas
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Número de receta debe ser único')
    ]
    
    def init(self):
        """Crear índices personalizados"""
        self.env.cr.execute("""
            CREATE INDEX IF NOT EXISTS pharmacy_prescription_active_idx
            ON pharmacy_prescription (patient_id, state, expiration_date)
            WHERE state IN ('validated', 'partially_dispensed')
        """)
```

#### 2. Campos Computados con Store

```python
# Campos que se usan frecuentemente deben almacenarse
total_amount = fields.Monetary(
    compute='_compute_total_amount',
    store=True,  # ← Almacenar en BD
    index=True   # ← Indexar para búsquedas
)

@api.depends('line_ids.subtotal')
def _compute_total_amount(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('subtotal'))
```

#### 3. Caché en POS

```javascript
// Cachear datos frecuentes en memoria
class PharmacyPOS extends POS {
    constructor() {
        super(...arguments);
        this.patientCache = new Map();
        this.prescriptionCache = new Map();
    }
    
    async getPatient(patientId) {
        // Revisar caché primero
        if (this.patientCache.has(patientId)) {
            return this.patientCache.get(patientId);
        }
        
        // Si no está, obtener del servidor
        const patient = await this.rpc({
            model: 'res.partner',
            method: 'read',
            args: [[patientId], ['name', 'allergies', 'insurance_info_ids']]
        });
        
        // Guardar en caché
        this.patientCache.set(patientId, patient[0]);
        return patient[0];
    }
}
```

#### 4. Búsquedas Optimizadas

```python
# ❌ MAL: Múltiples búsquedas
for order in orders:
    patient = self.env['res.partner'].search([('id', '=', order.partner_id.id)])
    insurance = self.env['pharmacy.insurance.info'].search([
        ('partner_id', '=', patient.id),
        ('active', '=', True)
    ], limit=1)

# ✅ BIEN: Una sola búsqueda con prefetch
orders = orders.with_context(prefetch_fields=True)
for order in orders:
    # Datos ya están en caché por prefetch
    patient = order.partner_id
    insurance = patient.insurance_info_ids.filtered('active')[:1]
```

#### 5. Queries SQL para Reportes

```python
# Para reportes complejos, usar SQL directo
def get_expiration_report(self, date_from, date_to):
    """Reporte de productos próximos a vencer"""
    self.env.cr.execute("""
        SELECT 
            pt.name AS product_name,
            sl.name AS lot_number,
            sl.expiration_date,
            SUM(sq.quantity) AS quantity_available,
            pt.standard_price * SUM(sq.quantity) AS total_value,
            EXTRACT(DAY FROM sl.expiration_date - CURRENT_DATE) AS days_to_expire
        FROM stock_lot sl
        JOIN product_product pp ON sl.product_id = pp.id
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        JOIN stock_quant sq ON sq.lot_id = sl.id
        WHERE sl.expiration_date BETWEEN %s AND %s
            AND sq.quantity > 0
            AND pt.is_pharmaceutical = TRUE
        GROUP BY pt.name, sl.name, sl.expiration_date, pt.standard_price
        ORDER BY sl.expiration_date ASC
    """, (date_from, date_to))
    
    return self.env.cr.dictfetchall()
```

---

## SEGURIDAD DE DATOS MÉDICOS

### Requisitos
- Datos de pacientes son sensibles (HIPAA-like compliance)
- Acceso controlado por roles
- Auditoría de accesos
- Encriptación de datos sensibles

### Implementación

#### 1. Control de Acceso Granular

```xml
<!-- security/security.xml -->
<record id="rule_patient_data_own" model="ir.rule">
    <field name="name">Usuarios ven solo sus pacientes asignados</field>
    <field name="model_id" ref="base.model_res_partner"/>
    <field name="domain_force">[
        '|',
        ('is_patient', '=', False),
        ('user_id', '=', user.id)
    ]</field>
    <field name="groups" eval="[(4, ref('pharmacy_group_user'))]"/>
</record>

<record id="rule_patient_data_pharmacist" model="ir.rule">
    <field name="name">Farmacéuticos ven pacientes de su farmacia</field>
    <field name="model_id" ref="base.model_res_partner"/>
    <field name="domain_force">[
        '|',
        ('is_patient', '=', False),
        ('company_id', '=', user.company_id.id)
    ]</field>
    <field name="groups" eval="[(4, ref('pharmacy_group_pharmacist'))]"/>
</record>
```

#### 2. Auditoría Automática

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def read(self, fields=None, load='_classic_read'):
        """Override read para auditar accesos a datos de pacientes"""
        result = super().read(fields, load)
        
        # Si es paciente, registrar acceso
        for record_data in result:
            if record_data.get('is_patient'):
                self.env['pharmacy.audit.log'].sudo().create({
                    'user_id': self.env.user.id,
                    'patient_id': record_data['id'],
                    'action': 'read',
                    'fields_accessed': str(fields),
                    'access_date': fields.Datetime.now(),
                    'ip_address': self.env.context.get('remote_addr', 'Unknown')
                })
        
        return result
```

#### 3. Encriptación de Campos Sensibles

```python
from cryptography.fernet import Fernet
import base64

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    allergies_encrypted = fields.Binary('Alergias Encriptadas')
    chronic_conditions_encrypted = fields.Binary('Condiciones Crónicas Encriptadas')
    
    def _get_encryption_key(self):
        """Obtener clave de encriptación desde configuración"""
        key = self.env['ir.config_parameter'].sudo().get_param('pharmacy.encryption_key')
        if not key:
            # Generar y guardar nueva clave
            key = Fernet.generate_key().decode()
            self.env['ir.config_parameter'].sudo().set_param('pharmacy.encryption_key', key)
        return key.encode()
    
    @api.depends('allergies_encrypted')
    def _compute_allergies(self):
        """Desencriptar alergias al leer"""
        f = Fernet(self._get_encryption_key())
        for record in self:
            if record.allergies_encrypted:
                try:
                    decrypted = f.decrypt(record.allergies_encrypted)
                    record.allergies = decrypted.decode()
                except:
                    record.allergies = ''
            else:
                record.allergies = ''
    
    def _inverse_allergies(self):
        """Encriptar alergias al escribir"""
        f = Fernet(self._get_encryption_key())
        for record in self:
            if record.allergies:
                encrypted = f.encrypt(record.allergies.encode())
                record.allergies_encrypted = encrypted
            else:
                record.allergies_encrypted = False
    
    allergies = fields.Text(
        compute='_compute_allergies',
        inverse='_inverse_allergies',
        store=False  # No almacenar sin encriptar
    )
```

#### 4. Logs de Auditoría

```python
class PharmacyAuditLog(models.Model):
    _name = 'pharmacy.audit.log'
    _description = 'Log de Auditoría de Accesos'
    _order = 'access_date desc'
    _rec_name = 'user_id'
    
    user_id = fields.Many2one('res.users', 'Usuario', required=True, index=True)
    patient_id = fields.Many2one('res.partner', 'Paciente', index=True)
    prescription_id = fields.Many2one('pharmacy.prescription', 'Receta', index=True)
    action = fields.Selection([
        ('read', 'Lectura'),
        ('write', 'Modificación'),
        ('create', 'Creación'),
        ('unlink', 'Eliminación'),
        ('print', 'Impresión'),
        ('export', 'Exportación'),
    ], required=True, index=True)
    fields_accessed = fields.Text('Campos Accedidos')
    access_date = fields.Datetime('Fecha de Acceso', required=True, index=True)
    ip_address = fields.Char('Dirección IP')
    session_id = fields.Char('ID de Sesión')
    reason = fields.Text('Motivo del Acceso')
    
    # Prevenir modificación de logs
    def write(self, vals):
        raise UserError(_('Los logs de auditoría no pueden ser modificados.'))
    
    def unlink(self):
        raise UserError(_('Los logs de auditoría no pueden ser eliminados.'))
```

---

## MULTI-SUCURSAL

### Configuración

```python
class PharmacyConfig(models.Model):
    _name = 'pharmacy.config'
    _description = 'Configuración de Farmacia'
    
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    warehouse_id = fields.Many2one('stock.warehouse', required=True)
    
    # Configuración de inventario
    auto_order_restock = fields.Boolean('Orden Automática de Resurtido', default=False)
    restock_warehouse_id = fields.Many2one('stock.warehouse', 'Almacén Central para Resurtido')
    
    # Configuración de POS
    pos_config_ids = fields.Many2many('pos.config', string='Puntos de Venta')
    
    # Configuración de delivery
    delivery_zones = fields.One2many('pharmacy.delivery.zone', 'pharmacy_config_id')
    
    # Configuración de seguros
    accepted_insurances = fields.Many2many('res.partner', string='Aseguradoras Aceptadas')
```

### Sincronización entre Sucursales

```python
class PharmacyStockMove(models.Model):
    _inherit = 'stock.move'
    
    def _action_done(self, cancel_backorder=False):
        """Override para notificar a otras sucursales"""
        result = super()._action_done(cancel_backorder)
        
        # Si producto está bajo en stock, notificar a almacén central
        for move in self:
            if move.product_id.is_pharmaceutical:
                available_qty = move.product_id.with_context(
                    warehouse=move.warehouse_id.id
                ).qty_available
                
                if available_qty < move.product_id.reorder_point:
                    self._notify_low_stock(move.product_id, move.warehouse_id)
        
        return result
    
    def _notify_low_stock(self, product, warehouse):
        """Notificar stock bajo a almacén central"""
        # Crear solicitud de resurtido automática
        config = self.env['pharmacy.config'].search([
            ('warehouse_id', '=', warehouse.id)
        ], limit=1)
        
        if config and config.auto_order_restock and config.restock_warehouse_id:
            # Crear transferencia interna
            picking_type = self.env['stock.picking.type'].search([
                ('warehouse_id', '=', config.restock_warehouse_id.id),
                ('code', '=', 'internal')
            ], limit=1)
            
            self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': config.restock_warehouse_id.lot_stock_id.id,
                'location_dest_id': warehouse.lot_stock_id.id,
                'move_ids': [(0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': product.reorder_quantity or 100,
                    'product_uom': product.uom_id.id,
                    'location_id': config.restock_warehouse_id.lot_stock_id.id,
                    'location_dest_id': warehouse.lot_stock_id.id,
                })]
            })
```

---

## CONFIGURACIÓN RECOMENDADA DE SERVIDOR

### Para 10,000 Transacciones Diarias

```ini
[options]
# Workers para multi-threading
workers = 8
max_cron_threads = 2

# Límites de memoria
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2 GB
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Base de datos
db_maxconn = 64
db_template = template0

# Logs
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log
logrotate = True

# Performance
unaccent = True
```

### PostgreSQL Tuning

```sql
-- postgresql.conf
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 128MB
max_connections = 200

-- Índices recomendados
CREATE INDEX CONCURRENTLY idx_pos_order_date ON pos_order(date_order);
CREATE INDEX CONCURRENTLY idx_prescription_patient_state ON pharmacy_prescription(patient_id, state);
CREATE INDEX CONCURRENTLY idx_stock_lot_expiration ON stock_lot(expiration_date) WHERE expiration_date IS NOT NULL;
```

---

## MONITOREO Y LOGS

### Logs Críticos

```python
import logging
_logger = logging.getLogger(__name__)

class PharmacyPrescription(models.Model):
    _name = 'pharmacy.prescription'
    
    def action_validate(self):
        """Validar receta con logging completo"""
        self.ensure_one()
        
        _logger.info(f"Iniciando validación de receta {self.name} para paciente {self.patient_id.name}")
        
        try:
            # Validaciones...
            self._check_interactions()
            self._check_allergies()
            self._check_contraindications()
            
            self.state = 'validated'
            
            _logger.info(f"Receta {self.name} validada exitosamente")
            
        except Exception as e:
            _logger.error(f"Error validando receta {self.name}: {str(e)}", exc_info=True)
            raise
```

### Métricas a Monitorear

```python
# Crear modelo para métricas
class PharmacyMetrics(models.Model):
    _name = 'pharmacy.metrics'
    _description = 'Métricas del Sistema'
    
    date = fields.Date(required=True, index=True)
    metric_type = fields.Selection([
        ('sales', 'Ventas'),
        ('prescriptions', 'Recetas'),
        ('deliveries', 'Entregas'),
        ('inventory', 'Inventario'),
    ], required=True)
    
    total_count = fields.Integer('Total')
    total_amount = fields.Monetary('Monto Total')
    average_time = fields.Float('Tiempo Promedio (seg)')
    error_count = fields.Integer('Errores')
    
    def _cron_collect_metrics(self):
        """Cron diario para recolectar métricas"""
        today = fields.Date.today()
        yesterday = today - timedelta(days=1)
        
        # Métricas de ventas POS
        orders = self.env['pos.order'].search([
            ('date_order', '>=', yesterday),
            ('date_order', '<', today)
        ])
        
        self.create({
            'date': yesterday,
            'metric_type': 'sales',
            'total_count': len(orders),
            'total_amount': sum(orders.mapped('amount_total')),
        })
        
        # Otras métricas...
```

---

**Estas especificaciones técnicas deben implementarse desde el inicio del desarrollo.**
