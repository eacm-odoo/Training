from odoo import models, fields, api


class Approvers(models.Model):
    _name = 'res.approvers'

    approver_id = fields.Many2one('res.users')
    record_id = fields.Integer('Rule Id')