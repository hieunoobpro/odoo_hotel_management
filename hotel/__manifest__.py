{
    'name': 'Hotel Management',
   'version': '1.0',
    'category': 'Custom',
    'author': 'Nguyen Duy Hieu',
    'summary': 'Manage hotels, rooms, and bookings',
    'description': 'A module to manage hotel operations including room management and bookings.',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hotel_views.xml',
        'views/room_views.xml',
        'views/booking_views.xml',
        'views/feature_views.xml',
        'views/menu_views.xml',
        'views/actions.xml',
    ],
    'installable': True,
    'application': True,
}