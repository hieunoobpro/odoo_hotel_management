from odoo import models, fields, api
from odoo.exceptions import UserError

class BookingService(models.Model):
    _name = 'booking.service'
    _description = 'Booking Service'

    name = fields.Char(string='Service Name', required=True)
    type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Product')
    ], string='Service Type', default='service', required=True)
    
    price = fields.Float(string='Price', required=True)
    quantity = fields.Integer(string='Quantity', default=1, required=True)
    description = fields.Char(string="Description", required=True)

    booking_ids = fields.Many2many(
        'room.booking', 'booking_service_rel', 'service_id', 'booking_id', string='Bookings'
    )
    
