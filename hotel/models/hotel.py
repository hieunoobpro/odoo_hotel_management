from odoo import models, fields, api
from odoo.exceptions import UserError

class HotelManagement(models.Model):
    _name = 'hotel.management'
    _description = 'Hotel Management'

    name = fields.Char(string='Hotel Name', required=True)
    code = fields.Char(string='Hotel Code', required=True, unique=True)
    address = fields.Text(string='Hotel Address')
    floors = fields.Integer(string='Number of Floors')
    total_rooms = fields.Integer(string='Total Rooms', compute='_compute_total_rooms', store=True)
    room_ids = fields.One2many('room.management', 'hotel_id', string='Rooms')
    active = fields.Boolean(string='Active', default=True)
    manager_id = fields.Many2one(
        'res.users', 
        string='Manager',
        domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)]
    )
    employee_ids = fields.One2many('hr.employee', 'hotel_id', string="Employees")

    @api.depends('room_ids')
    def _compute_total_rooms(self):
        for hotel in self:
            hotel.total_rooms = len(hotel.room_ids)
            
    def action_confirm_create(self):
        for record in self:
            if not record.name:
                raise UserError('Hotel Name is required!')
            record.active = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'hotel.management',
            'target': 'current',
        }
        
    def action_cancel(self):
        """Discard changes and return to the list view."""
        self.env['ir.ui.view'].clear_cache()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rooms',
            'res_model': 'room.management',
            'view_mode': 'list',
            'target': 'current',
        }
        
    _sql_constraints = [
        ('unique_hotel_code', 'unique(code)', 'Hotel code must be unique!')
    ]
  
