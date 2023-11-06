from odoo import fields, models, api

from datetime import date
from collections import Counter


class HrEmployeeMargin(models.Model):
    _name = 'hr.employee.margin'
    _description = 'Employee Margin'

    name = fields.Char()
    date = fields.Date(string='Date', required=True, copy=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, copy=True)
    job_id = fields.Many2one('hr.job', string='Job Position', copy=True)
    fls_geo_id = fields.Many2one('fls.geo', string='FLS GEO', copy=True)
    timesheet_manager_id = fields.Many2one('res.users', string='Timesheet Approver', copy=True)
    work_country_id = fields.Many2one('res.country', string='Work Country', copy=True)
    company_id = fields.Many2one('res.company', string='Company', copy=True)
            
    def _query_last_employee_margins(self):
        self._cr.execute(f"""
            SELECT DISTINCT ON (hr_employee.id)
                hr_employee_margin.*
            FROM hr_employee
            INNER JOIN hr_employee_margin
                ON hr_employee.id = hr_employee_margin.employee_id
            ORDER BY 
                hr_employee.id,
                hr_employee_margin.date DESC
        """)
        res = self._cr.dictfetchall()
        latest_margins ={}
        for em in res:
            latest_margins[em['employee_id']] = em
            if em['job_id'] == None:
                em['job_id'] = False
            if em['fls_geo_id'] == None:
                em['fls_geo_id'] = False
            if em['timesheet_manager_id'] == None:
                em['timesheet_manager_id'] = False
            if em['work_country_id'] == None:
                em['work_country_id'] = False
            if em['company_id'] == None:
                em['company_id'] = False
        return latest_margins

    @api.model
    def calculate_employee_margin(self, initialize=False):
        employees = self.env['hr.employee'].search([])
        latest_margins = self._query_last_employee_margins()
        margin_creations = []

        for employee_id in employees:
            margin_date = None
            if initialize:
                margin_date = date(2023, 1, 1)
            else:
                margin_date = date.today()
            if self.check_margin_differences(employee_id, latest_margins.get(employee_id.id, False)) or initialize:
                margin_creations.append({
                    'name': '{}-{}'.format(employee_id.name,margin_date),
                    'date': margin_date,
                    'employee_id': employee_id.id,
                    'job_id': employee_id.job_id.id,
                    'fls_geo_id': employee_id.fls_geo_id.id,
                    'timesheet_manager_id': employee_id.timesheet_manager_id.id,
                    'work_country_id': employee_id.work_country_id.id,
                    'company_id': employee_id.company_id.id
                })
        if len(margin_creations) > 0:
            self.env['hr.employee.margin'].create(margin_creations)

    def check_margin_differences(self, employee, last_margin):
        if last_margin:
            return not (
                employee.job_id.id == last_margin['job_id'] and
                employee.fls_geo_id.id == last_margin['fls_geo_id'] and
                employee.timesheet_manager_id.id == last_margin['timesheet_manager_id'] and
                employee.work_country_id.id == last_margin['work_country_id'] and
                employee.company_id.id == last_margin['company_id']
            )
        return True
