{
    'name': "GAB Reports Theme",
    'summary': """GAB Reports Theme DIN-5008 (Form B)""",
    #'description' :  """""",
    'version': '1.2',
    'category': 'Account',
    'author': 'Keller-MedienDesign & EDV-Dienstleistungen',
    'website': 'https://www.keller-mediendesign.de',
    'depends': ['l10n_de'],
    'data': [
        'views/assets.xml',
        'views/external_layout_din5008.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}