# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare, float_is_zero



class TestModel(models.Model):
    _name = "estate.property"
    _description = "Test Estate Property"
    _order = 'id desc'


    
    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description', default='When dublicated, Status and date are not copied.')
    postcode = fields.Char(string='postcode')
    date_availability = fields.Datetime(string='Available From', default=lambda self: fields.Datetime.now() + timedelta(days=90),readonly=True, copy=False)
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=False, copy=False)
    bedrooms = fields.Integer(string = 'Bed Rooms', default= 2)
    living_area = fields.Integer(string = 'Living Area (sqm)')
    facades = fields.Integer(string = 'Facades')
    garage = fields.Boolean(string = 'Garage')
    garden = fields.Boolean(string = 'Garden')
    garden_area = fields.Integer(string = 'Garden Area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection= [('north', 'North'), ('south', 'South'),
                    ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(string = 'Active', default=True)
    state = fields.Selection(
        [('new', 'New'),
         ('offer_received', 'Offer Received'),
         ('offer_accepted', 'Offer Accepted'),
         ('sold', 'Sold'),
         ('canceled', 'Canceled')],
        string='State', default='new', required=True, copy=False)

    
    def action_sold(self):
        self.ensure_one()
        if self.state == 'canceled':
            raise UserError("Cannot set a canceled property as sold.")
        self.state = 'sold'

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'sold':
            raise UserError("Cannot cancel a property that is already sold.")
        self.state = 'canceled'


    total_area = fields.Integer(string='Total Area (sqm)', compute='_compute_total_area', store=True)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for line in self:
            line.total_area = line.living_area + line.garden_area


    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False, default=lambda self: self.env.user)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', index=True)


 # New field for tags
    tag_ids = fields.Many2many('estate.property.tag', string='Tags', widget="many2many_tags")


 # New field for offers
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    
    best_price = fields.Float(string='Best Price', compute='_compute_best_price', store=True)


    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)


    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for property_record in self:
            # Retrieve the maximum price from the related offers
            property_record.best_price = max(property_record.offer_ids.mapped('price'), default=0.0)


    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''



    # Add SQL constraints
    _sql_constraints = [
        ('positive_expected_price', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive.'),
        ('positive_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must be positive.'),
        ('positive_offer_price', 'CHECK(price > 0)', 'Offer price must be strictly positive.'),
        ('unique_property_tag_name', 'UNIQUE(tag_ids.name)', 'Property tag name must be unique.'),
        ('unique_property_type_name', 'UNIQUE(property_type_id.name)', 'Property type name must be unique.'),
    ]

    # Add Python constraint
    @api.constrains('selling_price', 'expected_price')
    def check_selling_price(self):
        for rec in self:
            if not float_is_zero(rec.expected_price, precision_digits=2):
                percent_of_expected = rec.selling_price / rec.expected_price * 100
                if float_compare(percent_of_expected, 90, precision_digits=2) == -1:
                    raise ValidationError("The selling price must be at least 90% of the expected price.")


    @api.model
    def unlink(self):
        # Prevent deletion of properties not in 'New' or 'Canceled' state
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise exceptions.ValidationError("Cannot delete a property that is not in 'New' or 'Canceled' state.")
        return super(TestModel, self).unlink()

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'


    price = fields.Float(string='Price')
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], string='Status', copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)

    property_type_id = fields.Many2one('estate.property.type', string='Property Type', related='property_id.property_type_id', store=True)



    validity = fields.Integer(string='Validity(days)', default=7)
    date_deadline = fields.Date(string='Deadline', compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)
    create_date = fields.Datetime(string='Creation Date', readonly=True)

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.date_deadline = fields.Datetime.to_date(offer.create_date) + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                offer.validity = (fields.Datetime.to_datetime(offer.date_deadline) - fields.Datetime.to_datetime(offer.create_date)).days
            else:
                offer.validity = False


    def action_accept(self):
        self.ensure_one()
        if self.status != 'accepted':
            self.write({'status': 'accepted'})
            # Set buyer and selling price for the corresponding property
            self.property_id.buyer_id = self.partner_id.id
            self.property_id.selling_price = self.price
            
            # Make sure to handle the case where only one offer can be accepted in real life
            other_offers = self.property_id.offer_ids.filtered(lambda o: o.id != self.id)
            other_offers.action_refuse()

    def action_refuse(self):
        self.ensure_one()
        if self.status != 'refused':
            self.write({'status': 'refused'})




    # @api.multi
    # def unlink(self):
    #     for property_record in self:
    #         if property_record.state not in ('new', 'canceled'):
    #             raise exceptions.ValidationError("You cannot delete a property that is not in 'New' or 'Canceled' state.")
    #     return super(TestModel, self).unlink()



    @api.model
    def create(self, vals):

        if 'price' in vals:
            property_id = vals.get('property_id')
            existing_offer = self.search([('property_id', '=', property_id)], order='price desc', limit=1)
            if existing_offer and vals['price'] < existing_offer.price:
                raise UserError("Cannot create offer with lower amount than existing offer.")
        
        # Set property state to 'Offer Received'
        property_obj = self.env['estate.property'].browse(vals.get('property_id'))
        property_obj.write({'state': 'offer_received'})
        return super(EstatePropertyOffer, self).create(vals)




class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Add any additional fields for the buyer if needed

class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'salesperson_id', string='Properties', domain="[('state', 'in', ['new', 'offer_received', 'offer_accepted'])]")


    # Add any additional fields for the salesperson if needed
