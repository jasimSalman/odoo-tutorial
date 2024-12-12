from odoo import models, fields
from datetime import timedelta

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offers'
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string="Status", copy=False)

    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("real.estate.property", required=True)

    validity = fields.Integer(string="Validity", default=7)

    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_date_deadline",store=True)


    _sql_constraints = [
        ('price_positive', 
         'CHECK(price > 0)', 
         'Offer price must be strictly positive!'),
    ]


    def _compute_deadline(self):
        for record in self:
            if record.create_date and record.validity:
                record.date_deadline = timedelta(days=record.validity) + record.create_date 
            else:
                record.date_deadline = False

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                if record.create_date:
                    delta = record.date_deadline - record.create_date.date()
                    record.validity = delta.days
                else:
                    record.validity = 0
            else:
                record.validity = 0

    def action_refuse(self):
        for record in self:
            record.status = "refused"

    def action_confirm(self):
        for record in self:
            if record.status !="accepted":
                record.status = "accepted"
                record.property_id.selling_price = record.price
                record.property_id.buyer = self.env.user 

