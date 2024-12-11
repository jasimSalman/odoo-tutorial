from odoo import models, fields

class RealEstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tags'

    name = fields.Char(string="Name", required=True)


    _sql_constraints = [
        ('name_unique', 
         'UNIQUE(name)', 
         'Property Tag name must be unique!'),
    ]