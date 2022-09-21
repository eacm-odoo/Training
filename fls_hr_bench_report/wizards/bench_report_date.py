# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.tools.misc import format_date


class BenchReportDate(models.TransientModel):
    _name = 'hr.bench.report.date'
    _description = "Bench Report Date Selection"

    start_date = fields.Date(string="Start Date", default=fields.Datetime.today)
    end_date = fields.Date(string="End Date", default=lambda self: fields.Datetime.today() + relativedelta(weeks=4))

    def open_at_date(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name':
                _(
                    'Bench Report (%(start_date)s-%(end_date)s)',
                    start_date=format_date(self.env, self.start_date),
                    end_date=format_date(self.env, self.end_date)
                ),
            'res_model': 'hr.bench.report',
            'context':
                dict(
                    self.env.context,
                    date_start=self.start_date,
                    date_end=self.end_date,
                    search_default_employee=1,
                    search_default_report_date=2
                ),
        }
