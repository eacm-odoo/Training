from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    is_resource_manager = fields.Boolean(string="Is Resource Manager")    
    
    @api.depends('parent_id')
    def _compute_timesheet_manager(self):
        for employee in self:
            employee.timesheet_manager_id = False
            manager = employee.parent_id
            checked_managers = []
            while manager:
                if manager in checked_managers:
                    break
                if manager.user_id and manager.user_id.has_group('hr_timesheet.group_hr_timesheet_approver') and manager.is_resource_manager:
                    employee.timesheet_manager_id = manager.user_id
                    break
                checked_managers.append(manager)
                manager = manager.parent_id
