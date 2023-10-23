from odoo import fields, models, api, _


class FlsGeo(models.Model):
    _name = 'fls.geo'  
    _description='FLS GEO'

    name = fields.Char()
    