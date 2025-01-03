from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

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
    active = fields.Boolean(string='Active', default=True)

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
        self.env['ir.ui.view'].clear_cache()  # Clear cache to discard changes in the form

        # Return to the room list view
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
