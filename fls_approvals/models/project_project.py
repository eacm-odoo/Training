from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, values):
        if 'sale_line_id' in values:
            analytic_lines_to_preserve = self._get_validated_analytic_lines()
            result = super(ProjectProject, self).write(values)
            self._restore_preceding_sol_id(analytic_lines_to_preserve)
            return result
        else:
            return super(ProjectProject, self).write(values)

    def _get_validated_analytic_lines(self):
        '''Builds a map of validated analytic lines to their associated sale order line ids.'''
        analytic_lines_to_preserve = {}
        for project in self:
            validated_lines = self.env['account.analytic.line'].search([
                ('project_id', '=', project.id),
                ('validated', '=', True),
            ])
            analytic_lines_to_preserve.update({line.id: line.so_line.id for line in validated_lines})
        return analytic_lines_to_preserve

    def _restore_preceding_sol_id(self, analytic_lines_to_preserve):
        '''Restores the previous sale order line id for validated analytic lines.'''
        for line_id, old_so_line_id in analytic_lines_to_preserve.items():
            line = self.env['account.analytic.line'].browse(line_id)
            if line and line.so_line.id != old_so_line_id:
                line.write({
                    'freeze_so_line': True,
                    'so_line': old_so_line_id,
                })
