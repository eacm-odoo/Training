from odoo import fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError
from datetime import timedelta


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _timesheet_postprocess_values(self, values):
        result = {id_: {} for id_ in self.ids}
        sudo_self = self.sudo()  # this creates only one env for all operation that required sudo()
        # (re)compute the amount (depending on unit_amount, employee_id for the cost, and account_id for currency)
        ##### CUSTOM CODE START #####
        if any(field_name in values for field_name in ['unit_amount', 'employee_id', 'account_id', 'is_adjusted']):
            for timesheet in sudo_self:
                cost = timesheet._hourly_cost()
                amount = -timesheet.unit_amount * cost
                if values.get('is_adjusted') or (not values.get('is_adjusted') and self.is_adjusted):
                    amount = 0
                amount_converted = timesheet.employee_id.currency_id._convert(
                    amount, timesheet.account_id.currency_id or timesheet.currency_id, timesheet.company_id, timesheet.date)
                #####  CUSTOM CODE END  #####
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
    
    def action_add_time_to_timer(self, time):
        if self.validated:
            raise UserError(_('You cannot use the timer on validated timesheets.'))
        ##### CUSTOM CODE START #####
        if not self.user_id.sudo().employee_ids:
            #####  CUSTOM CODE END  #####
            raise UserError(_('An employee must be linked to your user to record time.'))
        timer = self.user_timer_id
        if not timer:
            self.action_timer_start()
            timer = self.user_timer_id
        timer.timer_start = min(timer.timer_start - timedelta(0, time), fields.Datetime.now())
    