# -*- coding: utf-8 -*-
from odoo import models, fields, api # type: ignore



class Budget(models.Model):
    _name = 'finanzas.budget'
    _description = 'Presupuesto por Departamento'
    
    name = fields.Char(string='Nombre del Presupuesto', required=True)
    department_id = fields.Many2one('hr.department', string='Departamento', required=True)
    year = fields.Integer(string='Año', required=True)
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Finalizado')
    ], string='Estado', default='draft')

    line_ids = fields.One2many('finanzas.budget.line', 'budget_id', string='Líneas de Presupuesto')

    @api.onchange('name', 'department_id', 'year')
    def _onchange_update_real_amount(self):
        """ Se ejecuta cuando se abre o cambia un presupuesto """
        for budget in self:
            for line in budget.line_ids:
                line._compute_real_amount()
             



class BudgetLine(models.Model):
    _name = 'finanzas.budget.line'
    _description = 'Línea de Presupuesto'
    
    budget_id = fields.Many2one('finanzas.budget', string='Presupuesto', required=True, ondelete='cascade')
    type = fields.Selection([
        ('income', 'Ingreso'),
        ('expense', 'Gasto')
    ], string='Tipo', required=True)
    planned_amount = fields.Float(string='Monto Planeado', required=True)
    
    real_amount = fields.Float(string='Monto Real', compute='_compute_real_amount', store=True)

    @api.depends('budget_id', 'budget_id.department_id', 'budget_id.year', 'type')
    def _compute_real_amount(self):
        for line in self:
            if line.budget_id:
                transactions = self.env['finanzas.financial.transaction'].search([
                    ('department_id', '=', line.budget_id.department_id.id),
                    ('type', '=', line.type),
                    ('date', '>=', '%s-01-01' % line.budget_id.year),
                    ('date', '<=', '%s-12-31' % line.budget_id.year)
                ])
                line.real_amount = sum(transactions.mapped('amount'))



class FinancialTransaction(models.Model):
    _name = 'finanzas.financial.transaction'
    _description = 'Transacción Financiera Real'

    name = fields.Char(string='Descripción', required=True)
    department_id = fields.Many2one('hr.department', string='Departamento', required=True)
    date = fields.Date(string='Fecha', required=True)
    type = fields.Selection([
        ('income', 'Ingreso'),
        ('expense', 'Gasto')
    ], string='Tipo', required=True)
    amount = fields.Float(string='Monto', required=True)

    @api.model
    def create(self, vals):
        """ Al crear una nueva transacción, actualiza automáticamente el presupuesto correspondiente. """
        transaction = super(FinancialTransaction, self).create(vals)
        transaction.update_budget_real_amount()
        return transaction

    def write(self, vals):
        """ Al modificar una transacción existente, actualiza el presupuesto correspondiente. """
        result = super(FinancialTransaction, self).write(vals)
        self.update_budget_real_amount()
        return result

    def unlink(self):
        """ Al eliminar una transacción, actualiza el presupuesto correspondiente. """
        self.update_budget_real_amount()
        return super(FinancialTransaction, self).unlink()

    def update_budget_real_amount(self):
        """ Encuentra el presupuesto correspondiente y actualiza el monto real. """
        for transaction in self:
            budget_lines = self.env['finanzas.budget.line'].search([
                ('budget_id.department_id', '=', transaction.department_id.id),
                ('budget_id.year', '=', transaction.date.year),
                ('type', '=', transaction.type)
            ])
            budget_lines._compute_real_amount()





"""

# -*- coding: utf-8 -*-  
# Importamos las clases necesarias de Odoo
from odoo import models, fields, api

# Definimos el modelo Budget (Presupuesto)
class Budget(models.Model):
    _name = 'finanzas.budget'  # Nombre técnico del modelo en Odoo
    _description = 'Presupuesto por Departamento'  # Descripción del modelo
    
    # Campos del modelo
    name = fields.Char(string='Nombre del Presupuesto', required=True)  # Nombre del presupuesto (obligatorio)
    department_id = fields.Many2one('hr.department', string='Departamento', required=True)  # Relación con un departamento (Many2one)
    year = fields.Integer(string='Año', required=True)  # Año del presupuesto (obligatorio)
    
    # Estado del presupuesto con selección de valores predefinidos
    state = fields.Selection([
        ('draft', 'Borrador'),  # Estado inicial
        ('confirmed', 'Confirmado'),  # Estado cuando se confirma
        ('done', 'Finalizado')  # Estado cuando se finaliza
    ], string='Estado', default='draft')  # Valor por defecto: 'draft'
    
    # Relación One2many con las líneas de presupuesto
    line_ids = fields.One2many('finanzas.budget.line', 'budget_id', string='Líneas de Presupuesto')

    # Método para comparar el presupuesto planeado con los gastos reales
    def action_compare_budget(self):
        for budget in self:  # Iteramos sobre cada presupuesto
            for line in budget.line_ids:  # Iteramos sobre cada línea de presupuesto
                # Calculamos el monto real sumando las transacciones financieras del departamento y tipo correspondiente
                total_real = sum(budget.env['finanzas.financial.transaction'].search([
                    ('department_id', '=', budget.department_id.id),  # Filtramos por el mismo departamento
                    ('type', '=', line.type),  # Filtramos por el mismo tipo (ingreso/gasto)
                    ('date', '>=', '%s-01-01' % budget.year),  # Filtramos por año desde el 1 de enero
                    ('date', '<=', '%s-12-31' % budget.year)  # Filtramos por año hasta el 31 de diciembre
                ]).mapped('amount'))  # Obtenemos los montos de las transacciones y los sumamos
                
                line.real_amount = total_real  # Asignamos el monto real calculado a la línea de presupuesto


# Definimos el modelo BudgetLine (Línea de Presupuesto)
class BudgetLine(models.Model):
    _name = 'finanzas.budget.line'  # Nombre técnico del modelo
    _description = 'Línea de Presupuesto'  # Descripción del modelo
    
    # Campos del modelo
    budget_id = fields.Many2one('finanzas.budget', string='Presupuesto', required=True, ondelete='cascade')  
    # Relación Many2one con el presupuesto al que pertenece (si el presupuesto se elimina, se eliminan sus líneas)
    
    type = fields.Selection([
        ('income', 'Ingreso'),  # Tipo ingreso
        ('expense', 'Gasto')  # Tipo gasto
    ], string='Tipo', required=True)  # Campo obligatorio para definir si es ingreso o gasto
    
    planned_amount = fields.Float(string='Monto Planeado', required=True)  # Monto planeado para esta línea
    
    real_amount = fields.Float(string='Monto Real', compute='_compute_real_amount', store=True)  
    # Monto real, calculado dinámicamente con `_compute_real_amount`, se almacena en la base de datos

    # Método que calcula el monto real basado en las transacciones financieras
    @api.depends('budget_id')  # Se ejecuta cuando cambia el presupuesto asociado
    def _compute_real_amount(self):
        for line in self:  # Iteramos sobre cada línea de presupuesto
            transactions = self.env['finanzas.financial.transaction'].search([
                ('department_id', '=', line.budget_id.department_id.id),  # Filtramos por el mismo departamento
                ('type', '=', line.type),  # Filtramos por el mismo tipo (ingreso/gasto)
                ('date', '>=', '%s-01-01' % line.budget_id.year),  # Filtramos desde el 1 de enero del año correspondiente
                ('date', '<=', '%s-12-31' % line.budget_id.year)  # Filtramos hasta el 31 de diciembre del mismo año
            ])
            line.real_amount = sum(transactions.mapped('amount'))  # Sumamos los montos de las transacciones encontradas


# Definimos el modelo FinancialTransaction (Transacción Financiera Real)
class FinancialTransaction(models.Model):
    _name = 'finanzas.financial.transaction'  # Nombre técnico del modelo
    _description = 'Transacción Financiera Real'  # Descripción del modelo
    
    # Campos del modelo
    name = fields.Char(string='Descripción', required=True)  # Descripción de la transacción (obligatorio)
    department_id = fields.Many2one('hr.department', string='Departamento', required=True)  # Departamento asociado a la transacción
    
    date = fields.Date(string='Fecha', required=True)  # Fecha de la transacción (obligatorio)
    
    type = fields.Selection([
        ('income', 'Ingreso'),  # Tipo ingreso
        ('expense', 'Gasto')  # Tipo gasto
    ], string='Tipo', required=True)  # Campo obligatorio para definir si es ingreso o gasto
    
    amount = fields.Float(string='Monto', required=True)  # Monto de la transacción

"""