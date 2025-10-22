from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestResPartner(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env['res.partner']

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

    def test_prescriber_with_license_success(self):
        """Test creación exitosa de médico con licencia"""
        doctor = self.Partner.create({
            'name': 'Dr. Test',
            'is_prescriber': True,
            'medical_license': 'MED-12345',
            'prescriber_specialty': 'general',
        })
        self.assertEqual(doctor.medical_license, 'MED-12345')
        self.assertEqual(doctor.prescriber_specialty, 'general')

    def test_laboratory_creation(self):
        """Test creación de laboratorio"""
        laboratory = self.Partner.create({
            'name': 'Test Laboratory',
            'is_company': True,
            'is_laboratory': True,
        })
        self.assertTrue(laboratory.is_laboratory)
        self.assertTrue(laboratory.is_company)

    def test_patient_medical_info(self):
        """Test que información médica de paciente se guarda correctamente"""
        patient = self.Partner.create({
            'name': 'Test Patient Medical',
            'is_patient': True,
            'allergies': 'Penicilina, Aspirina',
            'chronic_conditions': 'Diabetes, Hipertensión',
            'current_medications': 'Metformina 500mg',
        })
        self.assertEqual(patient.allergies, 'Penicilina, Aspirina')
        self.assertEqual(patient.chronic_conditions, 'Diabetes, Hipertensión')
        self.assertEqual(patient.current_medications, 'Metformina 500mg')

    def test_multiple_partner_types(self):
        """Test que un partner puede tener múltiples tipos"""
        partner = self.Partner.create({
            'name': 'Multi Type Partner',
            'is_company': True,
            'is_laboratory': True,
        })
        self.assertTrue(partner.is_company)
        self.assertTrue(partner.is_laboratory)
        self.assertFalse(partner.is_patient)
        self.assertFalse(partner.is_prescriber)