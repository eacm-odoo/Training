from odoo import models


class ProjectProductEmployeeMap(models.Model):
    _inherit = 'project.sale.line.employee.map'

    def write(self, values):
        result = super(ProjectProductEmployeeMap, self).write(values)
        if 'sale_line_id' in values:
            analytic_lines_to_preserve = self._get_validated_lines_to_preserve()
            self._restore_preceding_sol_id(analytic_lines_to_preserve)
        return result

    def _get_validated_lines_to_preserve(self):
        '''Builds a map of validated analytic lines to their associated sale order line ids.'''
        analytic_lines_to_preserve = {}
        for map_entry in self:
            validated_analytic_lines = self.env['account.analytic.line'].search([
                ('project_id', '=', map_entry.project_id.id),
                ('user_id', '=', map_entry.project_id.user_id.id),
                ('validated', '=', True)
            ])
            for line in validated_analytic_lines:
                analytic_lines_to_preserve[line.id] = line.so_line.id
        return analytic_lines_to_preserve

    def _restore_preceding_sol_id(self, analytic_lines_to_preserve):
        '''Restores the sale order line id for validated analytic lines; never updated ex post facto.'''
        for line_id, old_so_line_id in analytic_lines_to_preserve.items():
            line = self.env['account.analytic.line'].browse(line_id)
            if line.exists() and line.so_line.id != old_so_line_id:
                line.write({'prevent_so_line_update': True})
                line.sudo().write({'so_line': old_so_line_id})

