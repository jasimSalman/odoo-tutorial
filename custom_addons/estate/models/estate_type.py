from odoo import models, fields

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Types'
    _order = "name"

    name = fields.Char(string="Name", required=True)

    property_ids = fields.One2many("real.estate.property","property_type_id")

    sequence = fields.Integer(string="sequence", default=1)


    _sql_constraints = [
        ('name_unique', 
         'UNIQUE(name)', 
         'Property Type name must be unique!'),
    ]