from odoo import fields, models, _, api
from datetime import date
from odoo.osv import expression
from odoo.exceptions import AccessError

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _timesheet_postprocess_values(self, values):
        """ Get the addionnal values to write on record
            :param dict values: values for the model's fields, as a dictionary::
                {'field_name': field_value, ...}
            :return: a dictionary mapping each record id to its corresponding
                dictionary values to write (may be empty).
        """
        result = {id_: {} for id_ in self.ids}
        sudo_self = self.sudo()  # this creates only one env for all operation that required sudo()
        # (re)compute the amount (depending on unit_amount, employee_id for the cost, and account_id for currency)
        if any(field_name in values for field_name in ['unit_amount', 'employee_id', 'account_id', 'is_adjusted']):
            for timesheet in sudo_self:
                cost = timesheet._hourly_cost()
                amount = -timesheet.unit_amount * cost
                if values.get('is_adjusted') or (not values.get('is_adjusted') and self.is_adjusted):
                    amount = 0
                amount_converted = timesheet.employee_id.currency_id._convert(
                    amount, timesheet.account_id.currency_id or timesheet.currency_id, self.env.company, timesheet.date)
                result[timesheet.id].update({
                    'amount': amount_converted,
                })
        return result

    def _get_domain_for_validation_timesheets(self, validated=False):
        domain = [('is_timesheet', '=', True), ('validated', '=', validated)]
        if not self.user_has_groups('hr_timesheet.group_timesheet_manager'):
            ##### CUSTOM CODE START #####
            return expression.AND([domain, ['|', ('employee_id.timesheet_manager_id', '=', self.env.user.id),
                      '|', ('employee_id', 'in', self.env.user.employee_id.subordinate_ids.ids), 
                      ('employee_id.parent_id.user_id', '=', self.env.user.id)]])
            #####  CUSTOM CODE END  #####
        return domain
    