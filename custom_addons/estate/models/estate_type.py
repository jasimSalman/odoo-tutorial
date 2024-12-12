from odoo import models, fields, api

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Types'
    _order = "name"

    name = fields.Char(string="Name", required=True)

    property_ids = fields.One2many("real.estate.property","property_type_id")

    sequence = fields.Integer(string="sequence", default=1)

    offer_ids = fields.One2many("estate.property.offer", "property_id")

    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer_count", store=True)

    _sql_constraints = [
        ('name_unique', 
         'UNIQUE(name)', 
         'Property Type name must be unique!'),
    ]


    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)