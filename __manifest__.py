{
    'name': 'DBD Company Lookup (Open Data)',
    'version': '19.0',
    'license': 'OPL-1',
    'category': 'Contacts/Accounting/Localization/Master Data',
    'summary': 'Retrieve company information from DBD Open Data API with 13-digit tax ID.',
    'price': 19,
    'currency': 'USD',
    'support': 'aaccth.office@gmail.com',
    'depends': ['base', 'contacts'],
    'data': [
        'data/ir_config_parameter.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'images': ['static/description/banner.png'],
} 