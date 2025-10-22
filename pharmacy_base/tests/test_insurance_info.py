from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError
from datetime import date, timedelta


@tagged('post_install', '-at_install')
class TestInsuranceInfo(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.InsuranceInfo = cls.env['pharmacy.insurance.info']
        cls.Partner = cls.env['res.partner']

        # Crear paciente de prueba
        cls.patient = cls.Partner.create({
            'name': 'Test Patient',
            'is_patient': True,
        })

        # Crear aseguradora de prueba
        cls.insurance_company = cls.Partner.create({
            'name': 'Test Insurance Company',
            'is_company': True,
        })

    def test_create_insurance_info_success(self):
        """Test creación exitosa de información de seguro"""
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-12345',
            'member_id': 'MEM-67890',
            'plan_name': 'Plan Básico',
            'start_date': date.today(),
        })
        self.assertEqual(insurance.policy_number, 'POL-12345')
        self.assertEqual(insurance.member_id, 'MEM-67890')
        self.assertTrue(insurance.is_valid)

    def test_insurance_validation_dates(self):
        """Test validación de fechas de seguro"""
        with self.assertRaises(ValidationError):
            self.InsuranceInfo.create({
                'partner_id': self.patient.id,
                'insurance_company_id': self.insurance_company.id,
                'policy_number': 'POL-12345',
                'member_id': 'MEM-67890',
                'plan_name': 'Plan Básico',
                'start_date': date.today(),
                'end_date': date.today() - timedelta(days=1),  # End before start
            })

    def test_insurance_expired(self):
        """Test que seguro expirado no es válido"""
        past_date = date.today() - timedelta(days=10)
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-EXPIRED',
            'member_id': 'MEM-EXPIRED',
            'plan_name': 'Plan Expirado',
            'start_date': past_date - timedelta(days=365),
            'end_date': past_date,
        })
        self.assertFalse(insurance.is_valid)

    def test_insurance_future(self):
        """Test que seguro futuro no es válido"""
        future_date = date.today() + timedelta(days=10)
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-FUTURE',
            'member_id': 'MEM-FUTURE',
            'plan_name': 'Plan Futuro',
            'start_date': future_date,
        })
        self.assertFalse(insurance.is_valid)

    def test_calculate_patient_cost_full_coverage(self):
        """Test cálculo de costo con cobertura completa"""
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-FULL',
            'member_id': 'MEM-FULL',
            'plan_name': 'Plan Full Coverage',
            'start_date': date.today(),
            'annual_deductible': 100.0,
            'deductible_met': 100.0,  # Deducible ya pagado
            'copay_default': 0.0,
            'coinsurance_percentage': 0.0,
        })

        result = insurance.calculate_patient_cost(100.0)
        self.assertEqual(result['patient_pays'], 0.0)
        self.assertEqual(result['insurance_pays'], 100.0)

    def test_calculate_patient_cost_with_deductible(self):
        """Test cálculo de costo con deducible pendiente"""
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-DEDUCT',
            'member_id': 'MEM-DEDUCT',
            'plan_name': 'Plan con Deducible',
            'start_date': date.today(),
            'annual_deductible': 500.0,
            'deductible_met': 200.0,  # Le faltan 300 del deducible
            'copay_default': 0.0,
            'coinsurance_percentage': 20.0,
        })

        # Compra de 100, como queda deducible (300), todo va al deducible
        result = insurance.calculate_patient_cost(100.0)
        self.assertEqual(result['patient_pays'], 100.0)
        self.assertEqual(result['insurance_pays'], 0.0)
        self.assertEqual(result['reason'], 'Aplicado a deducible')

        # Compra de 500, 300 va al deducible, 200 con coseguro 20%
        result = insurance.calculate_patient_cost(500.0)
        expected_patient = 300.0 + (200.0 * 0.2)  # 300 deductible + 40 coinsurance
        expected_insurance = 200.0 * 0.8  # 160
        self.assertEqual(result['patient_pays'], expected_patient)
        self.assertEqual(result['insurance_pays'], expected_insurance)

    def test_calculate_patient_cost_invalid_insurance(self):
        """Test cálculo con seguro inválido"""
        # Crear seguro vencido
        past_date = date.today() - timedelta(days=10)
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-INVALID',
            'member_id': 'MEM-INVALID',
            'plan_name': 'Plan Inválido',
            'start_date': past_date - timedelta(days=365),
            'end_date': past_date,
        })

        result = insurance.calculate_patient_cost(100.0)
        self.assertEqual(result['patient_pays'], 100.0)
        self.assertEqual(result['insurance_pays'], 0.0)
        self.assertEqual(result['reason'], 'Cobertura no válida')

    def test_remaining_deductible_calculation(self):
        """Test cálculo de deducible restante"""
        insurance = self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-DEDUCT-CALC',
            'member_id': 'MEM-DEDUCT-CALC',
            'plan_name': 'Plan Deducible',
            'start_date': date.today(),
            'annual_deductible': 1000.0,
            'deductible_met': 300.0,
        })

        self.assertEqual(insurance.remaining_deductible, 700.0)

        # Actualizar deducible pagado
        insurance.deductible_met = 800.0
        self.assertEqual(insurance.remaining_deductible, 200.0)

    def test_unique_policy_member_combination(self):
        """Test que la combinación aseguradora-póliza-miembro es única"""
        self.InsuranceInfo.create({
            'partner_id': self.patient.id,
            'insurance_company_id': self.insurance_company.id,
            'policy_number': 'POL-UNIQUE',
            'member_id': 'MEM-UNIQUE',
            'plan_name': 'Plan Único',
            'start_date': date.today(),
        })

        with self.assertRaises(ValidationError):
            self.InsuranceInfo.create({
                'partner_id': self.patient.id,
                'insurance_company_id': self.insurance_company.id,
                'policy_number': 'POL-UNIQUE',  # Misma póliza
                'member_id': 'MEM-UNIQUE',     # Mismo miembro
                'plan_name': 'Plan Duplicado',
                'start_date': date.today(),
            })