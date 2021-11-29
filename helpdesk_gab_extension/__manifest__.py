# -*- coding: utf-8 -*-
{
    'name': "GAB Helpdesk Extension",

    'summary': """
        Extension for Odoo Enterprise Helpdesk module.
        Special requirements of gab company, https://www.gab.de/.
    """,

    'description': """
        Extension for Odoo Enterprise Helpdesk module.
        Special requirements of gab company, https://www.gab.de/.

        Extension details:
        - TODO
    """,

    'author': "gCoded - Sebastian Graup IT Consulting & Software Development",
    'website': "https://www.gcoded.de",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Helpdesk',
    'version': '0.13',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk', 'website', 'website_helpdesk', 'website_helpdesk_form'],

    # always loaded
    'data': [
        'data/website_helpdesk.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/custom_template_portal_helpdesk_ticket.xml',
        'views/custom_template_tickets_followup.xml',
        'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'auto_install': False,
    'installable': True
}