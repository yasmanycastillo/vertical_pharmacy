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