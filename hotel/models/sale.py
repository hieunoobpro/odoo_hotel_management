from odoo import models, exceptions, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def action_confirm(self):
        # Call the original action_confirm method to maintain standard behavior
        res = super(SaleOrder, self).action_confirm()
        
        for order in self:
            for line in order.order_line:
                product = line.product_id
                ordered_qty = line.product_uom_qty
                
                # Skip stock validation for service products
                if product.type == 'service':
                    continue
                
                # Check if there's enough stock to fulfill the order
                if product.qty_available < ordered_qty:
                    raise exceptions.UserError(
                        f"Not enough stock for {product.name}. "
                        f"Available quantity: {product.qty_available}, "
                        f"Ordered quantity: {ordered_qty}."
                    )
                # Subtract the ordered quantity from the product's on-hand quantity
                product.qty_available -= ordered_qty
                
            delivery_orders = self.env['stock.picking'].search([('origin', '=', order.name)])
            for delivery in delivery_orders:
                if delivery.state not in ['done', 'cancel']:
                    # Set quantities to reserved
                    delivery.action_assign()
                    # Validate the Delivery Order
                    if delivery.state == 'assigned':
                        delivery.button_validate()
                    else:
                        raise exceptions.UserError('Unable to validate the delivery order for %s.' % delivery.name)
        return res
