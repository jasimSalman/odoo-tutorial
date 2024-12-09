{
    'name': "Real Estate Managment System",
    'version': '1.0',
    'depends': ['base'],
    'author': "Jasim Salman",
    'category': 'estate',
    'description': """
    This is a estate managment system 
    """,
    'data': [
        'security/ir.model.access.csv',
        "views/estate_property_views.xml",
        "views/estate_menus.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}