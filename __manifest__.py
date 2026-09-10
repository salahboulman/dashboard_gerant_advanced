{
    'name': 'Dashboard Gérant Avancé',
    'version': '16.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Tableau de bord mobile épuré pour gérant (CA, Stock, Masarif, Commandes)',
    'author': 'WebPlus',
    'depends': ['base', 'point_of_sale', 'stock', 'account', 'pos_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/masarif_views.xml',
        'views/dashboard_template.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'price': 50.00,
    'currency': 'EUR',
}