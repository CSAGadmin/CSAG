{
    'name': "GAB Theme",
    'description': 'GAB Theme',
    'version': '1.0',
    'category': 'Theme/Corporate',
    'author': 'Keller-MedienDesign & EDV-Dienstleistungen',
    'website': 'https://www.keller-mediendesign.de',
    'depends': ['website', 'website_theme_install', 'helpdesk', 'portal', 'website_helpdesk', 'website_helpdesk_form'],
    'data': [
        # Attach Template
        'data/theme_gab_data.xml',

        # Attach Additional Website Elements
        'views/topmenu_language_switcher.xml',
        'views/footer.xml',
        'views/footer_awards.xml',
        'views/footer_copyright.xml',
        'views/footer_imprint_privacy.xml',
        'views/scroll_up_button.xml',
        'views/portal_layout.xml',
        'views/portal_my_home.xml',
        'views/helpdesk_team.xml',
        'views/helpdesk_ticket_submit.xml', #Vorraussetzung ist, dass es min. 1 eingerichtetes Kundendienst-Team mit Website-Formular-Freigabe gibt
        'views/helpdesk_ticket_submited.xml', #Vorraussetzung ist, dass es min. 1 eingerichtetes Kundendienst-Team mit Website-Formular-Freigabe gibt
        'views/helpdesk_ticket_rating_list.xml',
        'views/publish_management.xml',

        # Attach Error-Pages
        'views/403_error.xml',
        'views/404_error.xml',
        'views/500_error.xml',

        # Attach Custom Styles
        'views/assets.xml',
    ],
    'images': [
        'static/description/cover.png',
        'static/description/theme_screenshot.jpg',
    ],
    'application': False,
}