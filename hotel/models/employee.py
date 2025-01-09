from odoo import models, fields, api, _
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
        # Call the super method to create the employee
        employee = super(Employee, self).create(vals)
        
        # Check if an email is provided in vals
        if vals.get('work_email'):
            # Create a user with the email as login
            self.env['res.users'].create({
                'name': employee.name,  # Use the employee's name for the user
                'login': employee.work_email,  # Use the email as the login
                'email': employee.work_email,
                'employee_ids': [(4, employee.id)],  # Link the user to the employee
            })
        
        return employee