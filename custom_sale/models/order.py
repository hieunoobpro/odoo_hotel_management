from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        compute='_compute_amounts',
        tracking=5
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        store=True,
        compute='_compute_amounts'
    )
    amount_total = fields.Monetary(
        string="Total",
        store=True,
        compute='_compute_amounts',
        tracking=4
    )
    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True, ondelete='cascade')
    checkin_date = fields.Date(string="Check-in Date")
    checkout_date = fields.Date(string="Check-out Date")
    room_code = fields.Char(string="Room Code")
    customer_email = fields.Char(string="Customer Email")
    customer_phone = fields.Char(string="Customer Phone")
    
    def action_confirm(self):
        # Call the original action_confirm method
        res = super(SaleOrder, self).action_confirm()

        # Now update the related room booking statuses to "paid"
        for order in self:
            # Find related room bookings based on the sale order (assuming you have a Many2one field in RoomBooking)
            bookings = self.env['room.booking'].search([('sale_order_id', '=', order.id)])

            for booking in bookings:
                if booking.payment_status == 'unpaid':
                    # Update the payment status to "paid" and record payment date
                    booking.write({
                        'status': 'booked',
                        'payment_status': 'paid',
                        'payment_date': fields.Datetime.now(),
                        'payment_amount': order.amount_total  # Assuming the total amount is the payment
                    })

        return res

    @api.depends('order_line.price_subtotal', 'order_line.price_total', 'order_line.tax_id')
    def _compute_amounts(self):
        """Compute untaxed amount, tax, and total for sale orders."""
        for order in self:
            total_untaxed = 0.0
            total_tax = 0.0
            total_included = 0.0

            for line in order.order_line:
                if line.display_type == 'line_section':
                    continue
                
                # Add the subtotals and tax amounts from order lines
                total_untaxed += line.price_subtotal
                total_included += line.price_total

            # Calculate the total tax amount as the difference between total and untaxed
            total_tax = total_included - total_untaxed

            # Assign the computed values
            order.amount_untaxed = total_untaxed
            order.amount_tax = total_tax
            order.amount_total = total_included
