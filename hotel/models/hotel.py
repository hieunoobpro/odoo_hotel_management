from odoo import models, fields, api
from odoo.exceptions import ValidationError

# 1. Hotel Management Model
class HotelManagement(models.Model):
    _name = 'hotel.management'
    _description = 'Hotel Management'

    name = fields.Char(string='Hotel Name', required=True)
    code = fields.Char(string='Hotel Code', required=True, unique=True)
    address = fields.Text(string='Hotel Address')
    floors = fields.Integer(string='Number of Floors')
    total_rooms = fields.Integer(string='Total Rooms', compute='_compute_total_rooms', store=True)
    room_ids = fields.One2many('room.management', 'hotel_id', string='Rooms')

    @api.depends('room_ids')
    def _compute_total_rooms(self):
        for hotel in self:
            hotel.total_rooms = len(hotel.room_ids)

    _sql_constraints = [
        ('unique_hotel_code', 'unique(code)', 'Hotel code must be unique!')
    ]

# 2. Room Management Model
class RoomManagement(models.Model):
    _name = 'room.management'
    _description = 'Room Management'

    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True, ondelete='cascade')
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address', readonly=True)
    room_code = fields.Char(string='Room Code', required=True)
    bed_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Bed Type', required=True)
    price = fields.Float(string='Room Price', required=True)
    features_ids = fields.Many2many('room.feature', string='Room Features')
    status = fields.Selection([('available', 'Available'), ('booked', 'Booked')], string='Room Status', default='available')

    _sql_constraints = [
        ('unique_room_per_hotel', 'unique(hotel_id, room_code)', 'Room code must be unique within a hotel!')
    ]

# 3. Room Features Model
class RoomFeature(models.Model):
    _name = 'room.feature'
    _description = 'Room Features'

    name = fields.Char(string='Feature Name', required=True)

# 4. Room Booking Model
class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Room Booking'

    booking_code = fields.Char(string='Booking Code', required=True, unique=True)
    customer_name = fields.Char(string='Customer Name', required=True)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, required=True)
    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True)
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Room Type', required=True)
    room_id = fields.Many2one('room.management', string='Room', required=True)
    checkin_date = fields.Date(string='Check-in Date', required=True)
    checkout_date = fields.Date(string='Check-out Date', required=True)
    status = fields.Selection([('new', 'New'), ('confirmed', 'Confirmed')], string='Booking Status', default='new')

    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates(self):
        for record in self:
            if record.checkin_date > record.checkout_date:
                raise ValidationError('Check-in date must be before the check-out date!')

    _sql_constraints = [
        ('unique_booking_code', 'unique(booking_code)', 'Booking code must be unique!')
    ]
