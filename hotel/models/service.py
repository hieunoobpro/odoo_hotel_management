from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BookingService(models.Model):
    _name = 'booking.service'
    _description = 'Booking Service'

    name = fields.Char(string='Service Name', required=True)
    price = fields.Float(string='Price', required=True)
    quantity = fields.Integer(string='Quantity', default=1, required=True)  # Default = 1
    description = fields.Char(string='Service Description', required=True)
    booking_ids = fields.Many2many('booking.booking', 'booking_service_rel', 'service_id', 'booking_id', string='Bookings')
