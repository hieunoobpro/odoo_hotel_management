from odoo import models, fields, api

class RoomAvailabilityWizard(models.TransientModel):
    _name = 'room.availability.wizard'
    _description = 'Room Availability Wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def action_generate_report(self):
        # Lấy các phòng trống trong khoảng thời gian
        rooms = self.env['room.booking'].search([
            ('booking_ids.checkin_date', '>=', self.start_date),
            ('booking_ids.checkout_date', '<=', self.end_date),
        ])

        # Tạo context cho báo cáo
        return self.env.ref('hotel.report_room_availability').report_action(self, data={
            'rooms': rooms,
            'start_date': self.start_date,
            'end_date': self.end_date
        })
