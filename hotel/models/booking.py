from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

# 4. Room Booking Model
class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Room Booking'

    booking_code = fields.Char(string='Booking Code', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('room.booking'))
    customer_name = fields.Char(string='Customer Name', required=True)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, required=True)
    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True)
    hotel_name = fields.Char(related='hotel_id.name', string='Hotel Name', readonly=True)
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address', readonly=True)
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Room Type', required=True)
    room_id = fields.Many2one('room.management', string='Room', required=True, domain="[('hotel_id', '=', hotel_id), ('status', '=', 'available')]")
    room_code = fields.Char(related='room_id.room_code', string='Room Code', readonly=True)
    checkin_date = fields.Date(string='Check-in Date', required=True)
    checkout_date = fields.Date(string='Check-out Date', required=True)
    status = fields.Selection([('new', 'New'), ('booked', "Booked")], string='Booking Status', default='new')
    active = fields.Boolean(string='Active', default=True)

    @api.onchange('hotel_id')
    def _onchange_hotel_id(self):
        self.room_id = False
        return {'domain': {'room_id': [('hotel_id', '=', self.hotel_id.id), ('status', '=', 'available')]}}

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.room_type = self.room_id.bed_type

    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates(self):
        for record in self:
            if record.checkin_date > record.checkout_date:
                raise ValidationError('Check-in date must be before the check-out date!')
            
    @api.constrains('checkin_date', 'checkout_date', 'room_id')
    def _check_room_availability(self):
        for record in self:
            overlapping_bookings = self.env['room.booking'].search([
                ('room_id', '=', record.room_id.id),
                ('id', '!=', record.id),
                ('checkin_date', '<', record.checkout_date),
                ('checkout_date', '>', record.checkin_date),
                ('status', '!=', 'cancelled')
            ])
            if overlapping_bookings:
                raise ValidationError('The room is already booked for the selected dates.')       

    def action_confirm_create(self):
        
        for record in self:
            if not record.customer_name:
                raise UserError('Customer Name is required!')
            if record.status == 'new':
                record.status = 'booked'
            record.active = True

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'room.booking',
            'target': 'current',
        }
    

    _sql_constraints = [
        ('unique_booking_code', 'unique(booking_code)', 'Booking code must be unique!')
    ]