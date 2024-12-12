from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'real.estate.property',  
        'user_id',          
        string='Properties',
        domain=[('state', 'not in', ['sold', 'cancelled'])]
    )
