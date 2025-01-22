from datetime import timedelta
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
    customer_address = fields.Text(string='Customer Address')
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
    special_requests = fields.Text(string='Special Requests')
    checkin_date = fields.Datetime(string='Check-in Date', required=True)
    checkout_date = fields.Datetime(string='Check-out Date', required=True)
    service_ids = fields.Many2many('booking.service', 'booking_service_rel', 'booking_id', 'service_id', string='Services')
    status = fields.Selection([('new', 'New'), ('booked', "Booked")], string='Booking Status', default='new')
    active = fields.Boolean(string='Active', default=True)
    payment_status = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')], string='Payment Status', default='unpaid')
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    payment_method = fields.Selection([('credit_card', 'Credit Card'), ('cash', 'Cash'), ('bank_transfer', 'Bank Transfer')], string='Payment Method')
    payment_amount = fields.Float(string='Payment Amount', readonly=True)
    booking_product_ids = fields.One2many('booking.product', 'booking_id', string="Booking Products")
    free_product_ids = fields.One2many('booking.product', 'booking_id', string="Free Products", domain=[('price', '=', 0)])
    paid_product_ids = fields.One2many('booking.product', 'booking_id', string="Paid Products", domain=[('price', '>', 0)])
    
    normal_day_total = fields.Float(
        string='Total Normal Day Price',
        compute='_compute_booking_prices',
        store=True
    )

    weekend_total = fields.Float(
        string='Total Weekend Price',
        compute='_compute_booking_prices',
        store=True
    )

    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_booking_prices',
        store=True
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)  
    product_ids = fields.Many2many(
        'product.product', 
        string='Products',  # Use a domain if you want to filter by certain criteria
        help="Select the products for this booking"
    ) 
    quantity = fields.Integer(string="Quantity", default=1)
   
    @api.depends('checkin_date', 'checkout_date', 'room_price', 'booking_product_ids')
    def _compute_booking_prices(self):
        for record in self:
            total_days = 0
            weekend_days = 0
            normal_days = 0
            normal_price_total = 0.0
            weekend_price_total = 0.0
            service_cost = sum(product.quantity * product.price for product in record.booking_product_ids)

            if record.checkin_date and record.checkout_date:
                checkin = record.checkin_date.date()
                checkout = record.checkout_date.date()
                
                # Iterate over the days in the booking period
                current_date = checkin
                while current_date <= checkout:
                    total_days += 1
                    if current_date.weekday() in [5, 6]:  # Saturday (5) and Sunday (6)
                        weekend_days += 1
                    else:
                        normal_days += 1
                    current_date += timedelta(days=1)

                weekend_price = record.room_price * record.room_id.weekend_multiplier
                normal_price_total = normal_days * record.room_price
                weekend_price_total = weekend_days * weekend_price

            record.normal_day_total = normal_price_total
            record.weekend_total = weekend_price_total
            record.total_amount = normal_price_total + weekend_price_total + service_cost
            
    
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
                # Create a new Sale Order with additional details
                sale_order = self.env['sale.order'].create({
                    'partner_id': partner.id,
                    'origin': record.booking_code,
                    'user_id': self.env.user.id,  # Assign current user as salesperson
                    'company_id': self.env.company.id,  # Ensure correct company
                    'note': f"Booking Code: {record.booking_code}\n"
                            f"Hotel: {record.hotel_name}\n"
                            f"Check-in Date: {record.checkin_date}\n"
                            f"Check-out Date: {record.checkout_date}\n"
                            f"Room Code: {record.room_code}\n"
                            f"Customer Email: {record.customer_email}\n"
                            f"Customer Phone: {record.customer_phone}",
                })
            else:
                # Update the Sale Order details
                sale_order.partner_id = partner.id
                sale_order.note = (sale_order.note or '') + f"\nUpdated Booking: {record.booking_code}"

            # Handle Room Booking Line (if applicable)
            if record.room_code and record.checkin_date and record.checkout_date:
                duration = (record.checkout_date - record.checkin_date).days
                if duration <= 0:
                    raise UserError("Check-out date must be later than check-in date.")

                product = self.env['product.product'].search([('name', '=', "Booking")], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': "Booking",
                        'type': 'service',  # Assuming it's a service
                        'list_price': record.room_price,
                    })

                # Create or update sale order line for the room
                room_line = self.env['sale.order.line'].search([(
                    'order_id', '=', sale_order.id), ('product_id', '=', product.id)], limit=1)

                if room_line:
                    room_line.update({
                        'product_uom_qty': duration,
                        'price_unit': record.room_price,
                    })
                else:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'name': f"Room {record.room_code} Booking",
                        'product_uom_qty': duration,
                        'price_unit': record.room_price,
                        'product_id': product.id,
                    })

            # Add Products from booking_product_ids to Sale Order Lines
            for booking_product in record.booking_product_ids:  # Loop through the booking_product_ids field
                product = booking_product.product_id
                if product.type != 'service' and product.qty_available < booking_product.quantity:
                    raise UserError(f"Not enough stock for {product.name}. Available quantity: {product.qty_available}")

                existing_line = self.env['sale.order.line'].search([
                    ('order_id', '=', sale_order.id),
                    ('product_id', '=', product.id)
                ], limit=1)

                if existing_line:
                    # Update the existing line if it exists
                    existing_line.update({
                        'product_uom_qty': booking_product.quantity,  # Update quantity
                        'price_unit': booking_product.price,  # Update price
                    })
                else:
                    # Create sale order line for the product from booking_product
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'product_uom_qty': booking_product.quantity,  
                        'price_unit': booking_product.price,  
                        'name': product.name,
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
    
    # def action_confirm_payment(self):
    #     for record in self:
    #         if record.product_ids:
    #             for product in record.product_ids: 
    #                 stock_quant = self.env['stock.quant'].search([
    #                     ('product_id', '=', product.id),
    #                     ('location_id', '=', self.env.ref('stock.stock_location_stock').id)  # Default location
    #                 ], limit=1)
                    
    #                 if stock_quant:
    #                     # Log the current quantity before reducing
    #                     _logger.info("Product: %s, Current Quantity: %s", product.name, stock_quant.quantity)
                        
    #                     # Reduce the quantity
    #                     new_quantity = stock_quant.quantity - record.quantity
                        
    #                     # Log the new quantity after updating
    #                     _logger.info("Product: %s, New Quantity: %s", product.name, new_quantity)
                        
    #                     # Update the quantity
    #                     stock_quant.write({'quantity': new_quantity})

    #             # Optionally, you can also set the booking's status to "Paid"
    #             record.payment_status = 'paid'


    
    @api.model
    def create(self, vals):
        # Update the last rented date when a booking is made
        room = self.env['room.management'].browse(vals.get('room_id'))
        if room:
            room.write({'last_rented_date': fields.Date.today()})
        return super(RoomBooking, self).create(vals)

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

        if self.status == 'booked':
            self.room_id.write({'last_rented_date': self.checkout_date.date()})

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