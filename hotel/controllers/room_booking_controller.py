import logging
from odoo import http
from odoo.http import request

class RoomBookingController(http.Controller):
    _logger = logging.getLogger(__name__)

    @http.route(['/rooms'], type='http', auth="user", website=True)
    def portal_my_rooms(self, **kw):
        rooms = request.env['room.management'].search([
            ('status', '=', 'available')
        ])
        values = {
            'rooms': rooms,
        }
        return request.render("hotel.portal_my_rooms", values)

    @http.route(['/book/room/<int:room_id>'], type='http', auth="user", website=True)
    def portal_booking_form(self, room_id, **kw):
        room = request.env['room.management'].browse(room_id)
        booking_products = request.env['product.product'].search([])
        free_products = [product for product in booking_products if product.list_price == 0]
        additional_products = [product for product in booking_products if product.list_price > 0]

        values = {
            'room': room,
            'free_products': free_products,
            'additional_products': additional_products,
        }

        return request.render("hotel.portal_booking_form", values)

    @http.route(['/submit/booking'], type='http', auth="user", methods=['POST'], website=True)
    def submit_booking(self, **post):
        room_id = int(post.get('room_id'))
        hotel_id = int(post.get('hotel_id'))
        room_type = post.get('room_type')
        customer_name = post.get('customer_name')
        customer_email = post.get('customer_email')
        customer_phone = post.get('customer_phone')
        customer_address = post.get('customer_address')
        checkin_date = post.get('checkin_date')
        checkout_date = post.get('checkout_date')
        special_requests = post.get('special_requests')
        payment_method = post.get('payment_method')
        
        # Handle booking products
        booking_product_ids = []
        for product_id in request.httprequest.form.getlist('booking_product_ids'):
            quantity = int(post.get(f'quantity_{product_id}'))
            price = float(post.get(f'price_{product_id}'))
            booking_product_ids.append((0, 0, {
                'product_id': int(product_id),
                'quantity': quantity,
                'price': price,
            }))

        booking = request.env['room.booking'].create({
            'room_id': room_id,
            'hotel_id': hotel_id,
            'room_type': room_type,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'checkin_date': checkin_date,
            'checkout_date': checkout_date,
            'special_requests': special_requests,
            'payment_method': payment_method,
            'booking_product_ids': booking_product_ids,
        })

        return request.redirect('/my/bookings')

    @http.route(['/my/bookings'], type='http', auth="user", website=True)
    def portal_my_bookings(self, **kw):
        bookings = request.env['room.booking'].search([
            ('customer_email', '=', request.env.user.email),
        ])
        values = {
            'bookings': bookings,
        }
        return request.render("hotel.portal_my_bookings", values)