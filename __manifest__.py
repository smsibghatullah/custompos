# -*- coding: utf-8 -*-
{
    'name': "custom_point_of_sale",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','stock','point_of_sale'],

    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_point_of_sale/static/src/*/',  
        ],
          'web.assets_backend': [
            
        ],
        },
     
    'demo': [
        'demo/demo.xml',
    ],
}

