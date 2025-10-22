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