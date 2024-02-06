# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Real Estate',
    'version' : '1.2',
    'summary': 'Real Estate Software',
    'sequence': 15 ,
    'description': """ Real Estate Software""",
    'category': 'Productivity',
    'depends' : [],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type.xml',
        'views/estate_property_tag_views.xml',
        'views/res_users_views.xml',
        'views/estate_property_kanban.xml'
    ], 
    'demo': [],
    'installable': True,
    'application': True,
    'Auto_install': False,

}
