# -*- coding: utf-8 -*-
# from odoo import http
#  EJEMPLO DE CONTROLADOR DE RUTAS

# class Finanzas(http.Controller):
#     @http.route('/finanzas/finanzas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/finanzas/finanzas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('finanzas.listing', {
#             'root': '/finanzas/finanzas',
#             'objects': http.request.env['finanzas.finanzas'].search([]),
#         })

#     @http.route('/finanzas/finanzas/objects/<model("finanzas.finanzas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('finanzas.object', {
#             'object': obj
#         })

