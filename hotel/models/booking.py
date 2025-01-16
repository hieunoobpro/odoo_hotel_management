from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Room Booking'

    booking_code = fields.Char(string='Booking Code', required=True, copy=False, readonly=True, 
                               default=lambda self: self.env['ir.sequence'].next_by_code('room.booking'))
    customer_name = fields.Char(string='Customer Name', required=True)
    customer_email = fields.Char(string='Customer Email', required=True)
    customer_phone = fields.Char(string='Customer Phone', required=True)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today, required=True)
    hotel_id = fields.Many2one('hotel.management', string='Hotel', required=True)
    hotel_name = fields.Char(related='hotel_id.name', string='Hotel Name', readonly=True)
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address', readonly=True)
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double')], string='Room Type', required=True)
    room_id = fields.Many2one('room.management', string='Room', required=True, 
                              domain="[('hotel_id', '=', hotel_id), ('status', '=', 'available')]")
    room_code = fields.Char(related='room_id.room_code', string='Room Code', readonly=True)
    room_price = fields.Float(related='room_id.price', string='Room Price', readonly=True)
    service_ids = fields.Many2many('booking.service', 'booking_service_rel', 'booking_id', 'service_id', string='Services')
    checkin_date = fields.Datetime(string='Check-in Date', required=True)
    checkout_date = fields.Datetime(string='Check-out Date', required=True)
    status = fields.Selection([('new', 'New'), ('booked', "Booked")], string='Booking Status', default='new')
    active = fields.Boolean(string='Active', default=True)
    payment_status = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')], string='Payment Status', default='unpaid')
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    payment_amount = fields.Float(string='Payment Amount', readonly=True)
    
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)         
    
    def action_create_invoice(self):
        for record in self:
            if record.payment_status == 'paid':
                raise UserError("Payment has already been made for this booking.")
            
            # Search for an existing Sale Order by origin
            sale_order = self.env['sale.order'].search([('origin', '=', record.booking_code)], limit=1)
            
            # Search or create partner
            partner = self.env['res.partner'].search([('name', '=', record.customer_name)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': record.customer_name,
                    'email': record.customer_email,
                    'phone': record.customer_phone,
                })

            if not sale_order:
                # Create a new Sale Order if none exists
                sale_order = self.env['sale.order'].create({
                    'partner_id': partner.id,
                    'origin': record.booking_code,  # Booking code as origin
                })
            else:
                # Update the Sale Order partner if needed
                sale_order.partner_id = partner.id

            # Handle Room Booking Line
            if record.room_code and record.checkin_date and record.checkout_date:
                duration = (record.checkout_date - record.checkin_date).days
                if duration <= 0:
                    raise UserError("Check-out date must be later than check-in date.")
                
                sale_name = f"{record.room_code} {record.checkin_date.strftime('%d/%m')} - {record.checkout_date.strftime('%d/%m')}"
                product = self.env['product.product'].search([('name', '=', sale_name)], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': sale_name,
                        'type': 'service',
                        'list_price': record.total_amount,
                    })
                
                # Update or create sale order line for the room
                room_line = self.env['sale.order.line'].search([
                    ('order_id', '=', sale_order.id),
                    ('product_id', '=', product.id)
                ], limit=1)

                if room_line:
                    room_line.update({
                        'product_uom_qty': duration,
                        'price_unit': record.room_price,
                    })
                else:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'name': sale_name,
                        'product_uom_qty': duration,
                        'price_unit': record.room_price,
                        'product_id': product.id,
                    })

        # Handle Service Lines
        for service in record.service_ids:
            product_name = f"{service.name} - {service.description}"
            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': product_name,
                    'type': 'service',
                    'list_price': service.price,
                })

            # Search for an existing sale.order.line for this service
            service_line = self.env['sale.order.line'].search([
                ('order_id', '=', sale_order.id),
                ('product_id', '=', product.id)
            ], limit=1)

            if service_line:
                # Check for differences in quantity and price
                if service_line.product_uom_qty != service.quantity or service_line.price_unit != service.price:
                    service_line.update({
                        'product_uom_qty': service.quantity,
                        'price_unit': service.price,
                    })
            else:
                # Create a new line if it doesn't exist
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'name': product_name,
                    'product_uom_qty': service.quantity,
                    'price_unit': service.price,
                    'product_id': product.id,
                })

            # Link Sale Order to Booking
            record.sale_order_id = sale_order.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
        }
        
    @api.depends('checkin_date', 'checkout_date', 'room_price', 'service_ids.price')
    def _compute_total_amount(self):
        for record in self:
            room_cost = 0.0
            service_cost = sum(service.price for service in record.service_ids)

            if record.checkin_date and record.checkout_date and record.room_price:
                duration = (record.checkout_date - record.checkin_date).total_seconds() / 3600
                duration_in_days = duration / 24
                room_cost = max(duration_in_days, 1) * record.room_price

            record.total_amount = room_cost + service_cost
    
    @api.model
    def create(self, vals):
        booking = super(RoomBooking, self).create(vals)
        if booking.room_id:
            booking.room_id.last_rented_date = booking.checkout_date

        return booking
    
    @api.model
    def search_unpaid_bookings(self):
        return self.search([('payment_status', '=', 'unpaid')])
    
    @api.model
    def _get_manager_rule(self):
        return [
            ('hotel_id.manager_id', '=', self.env.user.id)
        ]

    @api.onchange('hotel_id')
    def _onchange_hotel_id(self):
        self.room_id = False
        self.room_code = False
        return {'domain': {'room_id': [('hotel_id', '=', self.hotel_id.id), ('status', '=', 'available')]}}

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.room_code = self.room_id.room_code
            self.room_type = self.room_id.bed_type
        else:
            self.room_code = False

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
            record.active = True

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'room.booking',
            'target': 'current',
        }
        
    def action_approve(self):
        for record in self:
            if record.status != 'new':
                raise UserError('Only bookings with status "New" can be approved.')
            record.write({'status': 'booked'})
            
    def action_pay(self):
        _logger.info("Payment button clicked. Opening wizard for booking %s", self.id)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'booking.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                'default_hotel_id': self.hotel_id.id,
                'default_room_id': self.room_id.id,
            }
        }

    _sql_constraints = [
        ('unique_booking_code', 'unique(booking_code)', 'Booking code must be unique!')
    ]