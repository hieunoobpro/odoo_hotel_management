{
    'name': 'Hotel Management',
   'version': '1.0',
    'category': 'Custom',
    'author': 'Nguyen Duy Hieu',
    'summary': 'Manage hotels, rooms, and bookings',
    'description': 'A module to manage hotel operations including room management and bookings.',
    'depends': ['base', 'hr', 'account', 'sale', "product", 'website', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/hotel_views.xml',
        'views/booking_pending_views.xml',
        'views/room_views.xml',
        'views/booking_views.xml',
        'views/feature_views.xml',
        'views/employee_views.xml',
        'views/service_views.xml',
        'views/payment_booking_wizard.xml',
        'views/product_views.xml',
        'views/menu_views.xml',
        'views/actions.xml',
        'views/sale_order_views.xml',
        'views/room_booking_views.xml',
        'report/booking_report.xml',
        'report/booking_report_template.xml',
        'data/favorite_filters.xml',
        'template/booking_portal_template.xml',
        'template/room_portal_template.xml',
        'template/room_booking_page.xml',
    
    ],
    'assets': {
        'web.report_assets_common': [
            'hotel/static/src/css/report_booking.css',
        ],
        'web.assets_frontend': [
            'hotel/static/src/css/booking_form.css',  # Ensure this line is present
        ],
    },

    'installable': True,
    'application': True,
}