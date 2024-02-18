# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Hamada Gym',
    'version' : '1.0',
    'summary': 'Hamada Gym Managment System',
    'sequence': 5 ,
    'description': """ Hamada Gym Managment System """,
    'category': 'Productivity',
    'depends' : [],
    'data': [
        'security/ir.model.access.csv',
        'views/trainer_views.xml',
    ], 
    'demo': [],
    'installable': True,
    'application': True,
    'Auto_install': False,

}
