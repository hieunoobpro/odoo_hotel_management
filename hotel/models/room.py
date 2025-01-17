from datetime import date, timedelta
import logging
from odoo import api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class RoomManagement(models.Model):
    _name = 'room.management'
    _description = 'Room Management'

    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True, ondelete='cascade')
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address', readonly=True)
    room_code = fields.Char(string='Room Code', required=True)
    bed_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Bed Type', required=True)
    price = fields.Float(string='Room Price', required=True)
    features_ids = fields.Many2many('room.feature', string='Room Features')
    last_rented_date = fields.Date(string='Last Rented Date') 
    status = fields.Selection([('available', 'Available'), ('booked', 'Booked')], string='Room Status', default='available')
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def update_room_status(self):
        # Get today's date
        today = date.today()
        rooms = self.search([])

        for room in rooms:
            # Check if there are any bookings for this room that overlap with today
            bookings = self.env['room.booking'].search([
                ('room_id', '=', room.id),
                ('checkin_date', '<=', today),
                ('checkout_date', '>=', today),
                ('status', '=', 'booked'),  # Assuming 'booked' status means it's occupied
            ])

            if bookings:
                room.status = 'booked'
            else:
                room.status = 'available'

        return True
    
    @api.model
    def find_unbooked_rooms(self):
        seven_days_ago = date.today() - timedelta(days=7)
        unbooked_rooms = self.search([
            ('status', '=', 'available'),
            ('last_rented_date', '<=', seven_days_ago)
        ])

        for room in unbooked_rooms:
            room_info = f"Room: {room.room_code}, Hotel: {room.hotel_id.name}"
            _logger.info(room_info)

        if not unbooked_rooms:
            _logger.info("No unbooked rooms found exceeding 7 days.")

    def action_confirm_create(self):
        for record in self:
            if not record.room_code:
                raise UserError('Room Name is required!')
            record.active = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'room.management',
            'target': 'current',
        }
        
    def action_cancel(self):
        self.env['ir.ui.view'].clear_cache() 

        return {
            'type': 'ir.actions.act_window',
            'name': 'Rooms',
            'res_model': 'room.management',
            'view_mode': 'list',
            'target': 'current',
        }

        
    _sql_constraints = [
        ('unique_room_per_hotel', 'unique(hotel_id, room_code)', 'Room code must be unique within a hotel!')
    ]
