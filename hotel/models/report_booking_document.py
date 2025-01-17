from datetime import date
from odoo import models, api
import locale
class ReportBookingDocument(models.AbstractModel):
    _name = 'report.hotel.report_booking_document'
    _description = 'Hotel Booking Confirmation Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        today = date.today()  # This is a datetime.date object
             # Force English locale for the date
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        return {
            'docs': self.env['room.booking'].browse(docids),
            'today': today,  # Pass the date object here
        }
