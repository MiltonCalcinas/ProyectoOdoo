# -*- coding: utf-8 -*-
from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError # type: ignore


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
        """ Se ejecuta al actualizar 'name', 'department_id', 'year' """
        for budget in self:
            for line in budget.line_ids:
                line._compute_real_amount()
             
    # valida la existencia de 1 ingreso y 1 gasto exactamente
    @api.constrains('line_ids')
    def _check_budget_lines(self):
        """ Verifica que el presupuesto tenga exactamente 1 ingreso y 1 gasto. """
        for budget in self:
            incomes = budget.line_ids.filtered(lambda l: l.type == 'income')
            expenses = budget.line_ids.filtered(lambda l: l.type == 'expense')

            if len(incomes) != 1 or len(expenses) != 1:
                raise ValidationError("Cada presupuesto debe contener exactamente un ingreso y un gasto.") # type: ignore


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



# store= True , en un campo calculado, el valor se guarda despues de ser calculado
# @api.depends('department_id','years') siginfica que el meétodo que esté debajo se ejecuta automáticamente cuando
# se modifica cualquiera de los dos campos indicados.
# self.env  propociona acceso al entorno de odoo como registro de otros modelos y recusos del sistema
class BudgetReport(models.Model):
    _name = 'finanzas.budget.report'
    _description = 'Reporte de Presupuesto y Transacciones'

    name = fields.Char(string='Nombre del Reporte', required=True)
    department_id = fields.Many2one('hr.department', string='Departamento', required=True)
    year = fields.Integer(string='Año', required=True)
    income_total = fields.Float(string='Total Ingresos', compute='_compute_totals', store=True)
    expense_total = fields.Float(string='Total Gastos', compute='_compute_totals', store=True)
    balance = fields.Float(string='Balance', compute='_compute_totals', store=True)
    income_real = fields.Float(string='Ingresos Reales', compute='_compute_totals', store=True)
    expense_real = fields.Float(string='Gastos Reales', compute='_compute_totals', store=True)
    balance_real = fields.Float(string='Balance Real', compute='_compute_totals', store=True)

    @api.depends('department_id', 'year')
    def _compute_totals(self):
        for report in self:
            # Filtrar las líneas de presupuesto por departamento y año
            budget_lines = self.env['finanzas.budget.line'].search([
                ('budget_id.department_id', '=', report.department_id.id),
                ('budget_id.year', '=', report.year)
            ])
            
            # Calcular los ingresos y gastos planeados
            report.income_total = sum(line.planned_amount for line in budget_lines if line.type == 'income')
            report.expense_total = sum(line.planned_amount for line in budget_lines if line.type == 'expense')
            
            # Calcular los ingresos y gastos reales
            report.income_real = sum(line.real_amount for line in budget_lines if line.type == 'income')
            report.expense_real = sum(line.real_amount for line in budget_lines if line.type == 'expense')
            
            # Calcular el balance (planeado y real)
            report.balance = report.income_total - report.expense_total
            report.balance_real = report.income_real - report.expense_real




    

