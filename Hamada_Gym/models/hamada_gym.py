# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare, float_is_zero



class SignInNewTrainers(models.Model):
    _name = "hamada.gym"
    _description = "Hamada Gym Managment System"


    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string = 'Age', required=True)
    gender = fields.Selection(
        string='Gender',
        selection= [('male', 'Male'), ('female', 'Female')], default='male')
    date_of_sign = fields.Date(string='Date Of Sign In The Gym', required=True, index=True,
                       default=lambda self: fields.Date.today())
    # your_date_field = fields.Date(string='Your string', default=datetime.today())
    phone_number = fields.Char(string='Phone Number', size = 11, required=True, default='01' )
    his_email = fields.Char(string='E-mail', default='@gmail.com')
    money_paid = fields.Integer(string = 'Money Paid', required = True)
    subscription = fields.Selection(
        string='Subscription',
        selection= [('1m', 'Month'), ('3m', '3 Months'),
                    ('6m', '6 Months'), ('y', 'Year')], default='3m', required=True)
    invitations = fields.Selection(
        string='Invitations',
        selection= [('1', '1'), ('3', '3'),
                    ('6', '6'), ('12', '12')], default='1')




    @api.onchange('subscription')
    def _onchange_subscription(self):
        if self.subscription == '1m':
            self.invitations = '1'
        elif self.subscription == '3m':
            self.invitations = '3'
        elif self.subscription == '6m':
            self.invitations = '6'
        elif self.subscription == 'y':
            self.invitations = '12'

    @api.onchange('money_paid')
    def _onchange_money_paid(self):
        if self.money_paid == 300:
            self.subscription = '1m'
        elif self.money_paid == 600:
            self.subscription = '3m'
        elif self.money_paid == 700:
            self.subscription = '6m'
        elif self.money_paid == 1500:
            self.subscription = 'y'


    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age < 13:
                raise ValidationError("Age must be at least 13 years old.")
