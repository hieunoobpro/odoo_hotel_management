from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_discount = fields.Monetary(string="Discount", default=0.0, help="Discount applied to the product price")
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal')

    @api.depends('product_id', 'product_uom_qty', 'price_unit', 'x_discount', 'order_id.currency_id')
    def _compute_amount(self):
        for line in self:
            discount_price = line.price_unit - line.x_discount
            # Calculate subtotal (before tax) using discounted price
            line.price_subtotal = discount_price * line.product_uom_qty
            taxes = line.tax_id.compute_all(discount_price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.price_total = taxes['total_included']
            
    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        # ensure_one() is a method that ensures that the recordset contains only one record.
        self.ensure_one() 
        # discount_amount or 0.0: if discount_amount is False, then 0.0
        price_unit_discount = self.price_unit - (self.x_discount or 0.0) 
        if price_unit_discount < 0:
            price_unit_discount = 0
        return super()._prepare_base_line_for_taxes_computation(**{
            'price_unit': price_unit_discount,
            **kwargs,
        })



            




