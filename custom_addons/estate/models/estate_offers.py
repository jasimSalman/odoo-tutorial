from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

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
    
    property_id = fields.Many2one("real.estate.property", required=True, ondelete="cascade")

    validity = fields.Integer(string="Validity", default=7)

    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_date_deadline",store=True)

    property_type_id = fields.Many2one(
        'estate.property.type', 
        related='property_id.property_type_id', 
        string="Property Type", 
        store=True
    )

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
                record.property_id.state = "offer accepted"
    
    @api.model
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            property_id = vals.get('property_id')
            if not property_id:
                raise UserError("Property ID is missing.")

            price = vals.get('price')
            if not price:
                raise UserError("Offer price is missing.")

            property_record = self.env['real.estate.property'].browse(property_id)
            if not property_record.exists():
                raise UserError("The property record does not exist.")

            property_record.state = 'offer received'
            existing_offers = self.env['estate.property.offer'].search([('property_id', '=', property_id)])
            _logger.info(f"Existing offers: {existing_offers}")

            for offer in existing_offers:
                _logger.info(f"Checking if new offer price {price} is less than existing offer price {offer.price}")
                if price < offer.price:
                    raise UserError(f"Your offer ({price}) is less than an existing offer ({offer.price}).")
        return super(RealEstatePropertyTypes, self).create(vals_list)