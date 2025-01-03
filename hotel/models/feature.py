from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

# 3. Room Features Model
class RoomFeature(models.Model):
    _name = 'room.feature'
    _description = 'Room Features'

    name = fields.Char(string='Feature Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    def action_confirm_create(self):
        for record in self:
            if not record.name:
                raise UserError('Feature Name is required!')
            record.active = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'room.feature',
            'target': 'current',
        }
      