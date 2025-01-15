from odoo import models, fields, api
from odoo.exceptions import UserError

class BookingPaymentWizard(models.TransientModel):
    _name = 'booking.payment.wizard'
    _description = 'Booking Payment Wizard'

    booking_id = fields.Many2one('room.booking', string="Booking")
    hotel_id = fields.Many2one('hotel.management', string="Hotel")
    room_id = fields.Many2one('room.management', string="Room ID")
    room_code = fields.Char(string='Room Code', related='room_id.room_code', readonly=True)
    room_price = fields.Float(related='room_id.price', string='Room Price', readonly=True)
    payment_amount = fields.Float(string="Payment Amount", required=True)
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today, readonly=True) 

    def action_confirm_payment(self):
        for wizard in self:
            if wizard.payment_amount <= 0:
                raise UserError("The payment amount must be greater than zero.")

            booking = wizard.booking_id
            booking.write({
                'payment_status': 'paid',  # Ensure you have a field payment_status in room.booking
                'payment_date': wizard.payment_date,
                'payment_amount': wizard.payment_amount
            })

        return {'type': 'ir.actions.act_window_close'}
