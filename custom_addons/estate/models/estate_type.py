from odoo import models, fields

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Types'

    name = fields.Char(string="Name", required=True)


    _sql_constraints = [
        ('name_unique', 
         'UNIQUE(name)', 
         'Property Type name must be unique!'),
    ]