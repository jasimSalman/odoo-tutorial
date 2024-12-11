from odoo import models, fields

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Types'

    name = fields.Char(string="name", required=True)
