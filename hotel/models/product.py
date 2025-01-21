from odoo import models, fields
class ProductProduct(models.Model):
    _inherit = "product.template"

    quantity_on_hand = fields.Float(
        string='Quantity on Hand',

        store=True
    )
