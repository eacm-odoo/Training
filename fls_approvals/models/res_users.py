from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    _order = 'order_seq'

    order_seq = fields.Integer(string="Override Ordering Sequence",default = 0)
