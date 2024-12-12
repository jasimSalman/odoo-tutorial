from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
import logging

class RealEstatePropertyTypes(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offers'
    _order = "price desc"
    _logger = logging.getLogger(__name__)

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
    
    @api.model
    def oncreate(self, vals):
        property_id = vals.get('property_id')
        self._logger.info(f"Received property_id: {property_id}")
        
        property_record = self.env['real.estate.property'].browse(property_id)
        self._logger.info(f"Property record: {property_record}")

        property_record.state = 'offer received'
        self._logger.info(f"Property state set to: {property_record.state}")

        existing_offers = self.env['estate.property.offer'].search([('property_id', '=', property_id)])
        self._logger.info(f"Existing offers: {existing_offers}")

        for offer in existing_offers:
            self._logger.info(f"Checking if new offer price {vals['price']} is less than existing offer price {offer.price}")
            if vals['price'] < offer.price:
                raise UserError("Your offer is less than the existing offers.")
        return super().create(vals)