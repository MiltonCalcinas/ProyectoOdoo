# -*- coding: utf-8 -*-
{
    'name': "finanzas",

    'summary': "Módulo para gestionar las finanzas de la empresa.",

    'description': """
    Este módulo permite a las empresas gestionar sus finanzas de manera eficiente, incluyendo la
    gestión de presupuestos, control de transacciones y generacion de reportes. 
    """,

    'author': "Milton y Talía",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contabilidad',
    'version': '0.1',

    # any module necessary for this one to work correctly
    #'depends': ['base'],
    'depends': ['base', 'hr'],


    # always loaded
    #'data': [
    #    'security/ir.model.access.csv',
    #    'views/views.xml',
    #    'views/templates.xml',
    #],

    'data': [
        'security/ir.model.access.csv',  # Se asegura que la seguridad esté cargada
        'views/budget_views.xml',  # Nueva vista para el presupuesto
        'views/budget_report_views.xml', # reporte
        'views/budget_line_views.xml',  # Nueva vista para lineas gasto/ingreso en presupuesto
        'views/financial_transaction_views.xml',  # Nueva vista para transacciones financieras
         'views/financial_transaction_menu.xml', # 
    ],


    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

