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

        Características principales:
        - Clasificación farmacéutica de productos
        - Gestión completa de pacientes con historial médico
        - Sistema de seguros con cálculo de copagos
        - Registro de médicos prescriptores
        - Laboratorios y control de productos
    """,
    'author': 'Vertical Pharmacy Team',
    'website': 'https://github.com/vertical-pharmacy',
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
    'images': ['static/description/main.png'],
}