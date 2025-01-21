from odoo import models, fields, api

class BookingProduct(models.Model):
    _name = 'booking.product'
    _description = 'Booking Product'

    booking_id = fields.Many2one('room.booking', string="Booking", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Integer(string="Quantity", required=True)
    price = fields.Float(string="Price", related='product_id.list_price', readonly=True)