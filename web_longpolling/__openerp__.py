{
    'name': 'Long polling',
    'version': '1.0.0',
    'sequence': 150,
    'category': 'Anybox',
    'description': """
    """,
    'author': 'Anybox',
    'website': 'http://anybox.fr',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'js': [
        'static/src/js/longpolling.js',
    ],
    'installable': True,
}
