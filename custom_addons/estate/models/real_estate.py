from odoo import models, fields,api
from datetime import datetime , timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Real Estate Property'   
    _order = "id desc" 

    name = fields.Char(string="title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available from", copy=False, default=lambda self: self._default_date_availability())
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True , copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string="Garden Orientation"
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer received', 'Offer Received'),
            ('offer accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        copy=False,
        default="new",
        string="Status"
    )

    property_type_id = fields.Many2one("estate.property.type", string="Types")
    
    seller = fields.Many2one("res.partner", string="Salesman", default=lambda self: self.env.user.partner_id)

    buyer = fields.Many2one("res.users", string="Buyer", copy=False)

    tag_ids = fields.Many2many(
        'estate.property.tag', 
        string="Tags", 
    )

    offer_ids = fields.One2many("estate.property.offer", "property_id")

    total_area = fields.Float(compute="_compute_total_area", string="Total Area")

    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    user_id = fields.Many2one(
        'res.users',  
        string="Salesperson")


    _sql_constraints = [
        ('expected_price_positive', 
        'CHECK(expected_price > 0)', 
        'Expected Price must be strictly positive!'),
    ]


    def _default_date_availability(self):
        return datetime.today() + timedelta(days=90)

    @api.depends("living_area" ,"garden_area")
    def _compute_total_area (self):
        for recod in self:
            recod.total_area = recod.living_area + recod.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                prices = record.offer_ids.mapped("price")
                record.best_price = max(prices) if prices else 0
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else :
            self.garden_area = 0
            self.garden_orientation = False

    def cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("A sold property cannot be cancelled.")
            if record.state != 'cancelled':
                record.state = 'cancelled'

    def sold_property(self):
       for record in self:
            if record.state == 'cancelled':
                raise UserError("A cancelled property cannot be set as sold.")
            if record.state != 'sold':
                record.state = 'sold'

    @api.constrains("selling_price", "expected_price", "offer_ids")
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError(('The selling price cannot be lower than 90% of the expected price.'))

    def unlink(self, **kwargs):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError("You cannot delete this property.")
        return super().unlink(**kwargs)
