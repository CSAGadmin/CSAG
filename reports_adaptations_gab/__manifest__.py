{
    'name': "GAB Reports Adaptations",
    'summary': """GAB Reports Adaptations""",
    #'description' :  """""",
    'version': '1.1',
    'category': 'Account',
    'author': 'Keller-MedienDesign & EDV-Dienstleistungen',
    'website': 'https://www.keller-mediendesign.de',
    'depends': ['account', 'sale'],
    'data': [
        'views/report_invoice_document.xml',
        'views/report_saleorder_document.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}