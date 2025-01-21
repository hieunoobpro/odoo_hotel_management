from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = 'hr.employee'


    hotel_id = fields.Many2one(
        comodel_name='hotel.management',
        string="Hotel",
        help="The hotel this employee is assigned to"
    )

    @api.model
    def create(self, vals):
        employee = super(Employee, self).create(vals)
        
        if vals.get('work_email'):
            self.env['res.users'].create({
                'name': employee.name,
                'login': employee.work_email,
                'email': employee.work_email,
                'employee_ids': [(4, employee.id)],  
            })
        
        return employee