from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Identificación Farmacéutica
    is_pharmaceutical = fields.Boolean(
        string='Es Farmacéutico',
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