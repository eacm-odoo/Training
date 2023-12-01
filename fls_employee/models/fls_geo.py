from odoo import fields, models


class FlsGeo(models.Model):
    _name = 'fls.geo'  
    _description='FLS GEO'

    name = fields.Char()
    user_id = fields.Many2one('res.users', string="Responsible")
    