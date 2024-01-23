from odoo import models


class ProjectProductEmployeeMap(models.Model):
    _inherit = 'project.sale.line.employee.map'

    def write(self, values):
        if 'sale_line_id' in values:
            analytic_lines_to_preserve = self._get_validated_analytic_lines()
            result = super(ProjectProductEmployeeMap, self).write(values)
            self._restore_preceding_sol_id(analytic_lines_to_preserve)
            return result
        else:
            return super(ProjectProductEmployeeMap, self).write(values)

    def _get_validated_analytic_lines(self):
        '''Builds a map of validated analytic lines to their associated sale order line ids.'''
        analytic_lines_to_preserve = {}
        for map_entry in self:
            validated_lines = self.env['account.analytic.line'].search([
                ('project_id', '=', map_entry.project_id.id),
                ('user_id', '=', map_entry.project_id.user_id.id),
                ('validated', '=', True)
            ])
            analytic_lines_to_preserve.update({line.id: line.so_line.id for line in validated_lines})
        return analytic_lines_to_preserve

    def _restore_preceding_sol_id(self, analytic_lines_to_preserve):
        '''Restores the sale order line id for validated analytic lines; never updated ex post facto.'''
        for line_id, old_so_line_id in analytic_lines_to_preserve.items():
            line = self.env['account.analytic.line'].browse(line_id)
            if line and line.so_line.id != old_so_line_id:
                line.freeze_so_line = True
                line.so_line = old_so_line_id

