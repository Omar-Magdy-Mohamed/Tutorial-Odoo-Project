# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare, float_is_zero



class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        # Add a print statement to ensure this method is being called
        # print("Custom action_sold method is called")
        
        # Retrieve the partner ID from the current estate.property
        partner_id = self.buyer_id.id

        move_obj = self.env['account.move']
        move_type = self.env.ref('account.data_account_type_receivable')
        values = {
    'partner_id': partner_id,
    'move_type': 'out_invoice',  # Corresponds to a 'Customer Invoice'
    # Add other required fields as needed
}
        move = move_obj.create(values)




        # Add invoice lines
        invoice_lines = []
        for property in self:
            # Calculate invoice line values
            price = property.selling_price * 0.06 + 100.00
            name = f"Property: {property.name}"  # Example name for the invoice line
            quantity = 1  # Assuming one unit for each property

            # Create invoice line values dictionary
            invoice_line_values = {
                'name': name,
                'quantity': quantity,
                'price_unit': price,
                # Add other required fields as needed
        }
            invoice_lines.append((0, 0, invoice_line_values))

        # Update the invoice with the invoice lines
        move.update({
                'invoice_line_ids': invoice_lines
        })


        # Return the super call to maintain the original behavior
        return super(EstateProperty, self).action_sold()