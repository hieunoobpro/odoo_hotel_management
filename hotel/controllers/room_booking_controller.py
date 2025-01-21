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
        services = request.env['booking.service'].search([])
        values = {
            'room': room,
            'services': services,
        }
        return request.render("hotel.portl_abooking_form", values)

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
        service_ids = post.get('services', [])
        if isinstance(service_ids, str):
            service_ids = [int(service_ids)]
        elif isinstance(service_ids, list):
            service_ids = [int(service_id) for service_id in service_ids]

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
            'service_ids': [(6, 0, service_ids)],
        })

        return request.redirect('/my/bookings')
    
    @http.route(['/my/bookings'], type='http', auth="user", website=True)
    
    def portal_my_bookings(self, **kw):

        bookings = request.env['room.booking'].search([
            ('customer_email', '=', request.env.user.email),
        ])
        print(f"Fetching bookings for customer: {bookings.customer_email}")

        values = {
            'bookings': bookings,
        }
        
        return request.render("hotel.portal_my_bookings", values)
           
