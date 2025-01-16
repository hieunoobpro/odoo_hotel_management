{
    'name': 'Hotel Management',
   'version': '1.0',
    'category': 'Custom',
    'author': 'Nguyen Duy Hieu',
    'summary': 'Manage hotels, rooms, and bookings',
    'description': 'A module to manage hotel operations including room management and bookings.',
    'depends': ['base', 'hr'],
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
        'views/menu_views.xml',
        'views/actions.xml',
        'data/favorite_filters.xml'
    ],
    'installable': True,
    'application': True,
}