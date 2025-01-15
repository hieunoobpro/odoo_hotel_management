from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        compute='_compute_amounts',
        tracking=5
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        store=True,
        compute='_compute_amounts'
    )
    amount_total = fields.Monetary(
        string="Total",
        store=True,
        compute='_compute_amounts',
        tracking=4
    )

    @api.depends('order_line.price_subtotal', 'order_line.price_total', 'order_line.tax_id')
    def _compute_amounts(self):
        """Compute untaxed amount, tax, and total for sale orders."""
        for order in self:
            total_untaxed = 0.0
            total_tax = 0.0
            total_included = 0.0

            for line in order.order_line:
                if line.display_type == 'line_section':
                    continue
                
                # Add the subtotals and tax amounts from order lines
                total_untaxed += line.price_subtotal
                total_included += line.price_total

            # Calculate the total tax amount as the difference between total and untaxed
            total_tax = total_included - total_untaxed

            # Assign the computed values
            order.amount_untaxed = total_untaxed
            order.amount_tax = total_tax
            order.amount_total = total_included
