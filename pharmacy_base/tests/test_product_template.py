from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestProductTemplate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env['product.template']
        cls.Category = cls.env['product.category']

        # Crear categoría de prueba
        cls.category_pharma = cls.Category.create({
            'name': 'Test Pharma Category',
            'pharmaceutical_category': 'prescription',
        })

        cls.category_otc = cls.Category.create({
            'name': 'Test OTC Category',
            'pharmaceutical_category': 'otc',
        })

    def test_pharmaceutical_product_requires_active_principle(self):
        """Test que productos farmacéuticos requieren principio activo"""
        with self.assertRaises(ValidationError):
            self.ProductTemplate.create({
                'name': 'Test Product',
                'is_pharmaceutical': True,
                'categ_id': self.category_pharma.id,
                # Falta active_principle
            })

    def test_create_pharmaceutical_product_success(self):
        """Test creación exitosa de producto farmacéutico"""
        product = self.ProductTemplate.create({
            'name': 'Test Pharma Product',
            'is_pharmaceutical': True,
            'active_principle': 'Paracetamol',
            'categ_id': self.category_pharma.id,
        })
        self.assertTrue(product.requires_prescription)
        self.assertEqual(product.active_principle, 'Paracetamol')

    def test_otc_product_no_prescription_required(self):
        """Test que productos OTC no requieren receta"""
        product = self.ProductTemplate.create({
            'name': 'Test OTC Product',
            'is_pharmaceutical': True,
            'active_principle': 'Ibuprofeno',
            'categ_id': self.category_otc.id,
        })
        self.assertFalse(product.requires_prescription)

    def test_related_products(self):
        """Test productos relacionados funcionan correctamente"""
        product1 = self.ProductTemplate.create({
            'name': 'Product 1',
            'is_pharmaceutical': True,
            'active_principle': 'Principle A',
            'categ_id': self.category_otc.id,
        })

        product2 = self.ProductTemplate.create({
            'name': 'Product 2',
            'is_pharmaceutical': True,
            'active_principle': 'Principle B',
            'categ_id': self.category_otc.id,
        })

        product1.related_products_ids = [(4, product2.id)]
        self.assertIn(product2, product1.related_products_ids)

    def test_pharmaceutical_form_selection(self):
        """Test que las formas farmacéuticas son válidas"""
        product = self.ProductTemplate.create({
            'name': 'Test Product with Form',
            'is_pharmaceutical': True,
            'active_principle': 'Test Principle',
            'pharmaceutical_form': 'tableta',
            'concentration': '500mg',
            'presentation': 'Caja con 20 tabletas',
            'categ_id': self.category_otc.id,
        })
        self.assertEqual(product.pharmaceutical_form, 'tableta')
        self.assertEqual(product.concentration, '500mg')