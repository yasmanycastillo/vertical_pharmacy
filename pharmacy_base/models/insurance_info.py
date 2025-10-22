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