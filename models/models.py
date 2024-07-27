from odoo import api, fields, models

from odoo.exceptions import UserError
from itertools import groupby
from operator import itemgetter
from datetime import date

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
   
    _inherit = 'res.config.settings'

    pos_stock_quant_id = fields.Many2one( related='pos_config_id.pos_stock_id', readonly=False, string="Location")

    
class ProductProduct(models.Model):
    _inherit = 'pos.config'

    pos_stock_id = fields.Many2one('stock.location', readonly=False, string="Location")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_info_pos(self, price, quantity, pos_config_id):
        self.ensure_one()
        config = self.env['pos.config'].browse(pos_config_id)
        stock_quants = self.env['stock.quant'].search([
                ('product_id', '=', self.id),
            ])

        locations = [{
        'location_id': quant.location_id.complete_name,
        'inventory_quantity': quant.inventory_quantity_auto_apply,
         } for quant in stock_quants]
        print(locations,"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")


        # Tax related
        taxes = self.taxes_id.compute_all(price, config.currency_id, quantity, self)
        grouped_taxes = {}
        for tax in taxes['taxes']:
            if tax['id'] in grouped_taxes:
                grouped_taxes[tax['id']]['amount'] += tax['amount']/quantity if quantity else 0
            else:
                grouped_taxes[tax['id']] = {
                    'name': tax['name'],
                    'amount': tax['amount']/quantity if quantity else 0
                }

        all_prices = {
            'price_without_tax': taxes['total_excluded']/quantity if quantity else 0,
            'price_with_tax': taxes['total_included']/quantity if quantity else 0,
            'tax_details': list(grouped_taxes.values()),
        }

        # Pricelists
        if config.use_pricelist:
            pricelists = config.available_pricelist_ids
        else:
            pricelists = config.pricelist_id
        price_per_pricelist_id = pricelists._price_get(self, quantity) if pricelists else False
        pricelist_list = [{'name': pl.name, 'price': price_per_pricelist_id[pl.id]} for pl in pricelists]

        # Warehouses
        warehouse_list = [
            {'name': w.name,
            'available_quantity': self.with_context({'warehouse': w.id}).qty_available,
            'forecasted_quantity': self.with_context({'warehouse': w.id}).virtual_available,
            'uom': self.uom_name}
            for w in self.env['stock.warehouse'].search([])]

        # Suppliers
        key = itemgetter('partner_id')
        supplier_list = []
        for key, group in groupby(sorted(self.seller_ids, key=key), key=key):
            for s in list(group):
                if not((s.date_start and s.date_start > date.today()) or (s.date_end and s.date_end < date.today()) or (s.min_qty > quantity)):
                    supplier_list.append({
                        'name': s.partner_id.name,
                        'delay': s.delay,
                        'price': s.price
                    })
                    break

        # Variants
        variant_list = [{'name': attribute_line.attribute_id.name,
                         'values': list(map(lambda attr_name: {'name': attr_name, 'search': '%s %s' % (self.name, attr_name)}, attribute_line.value_ids.mapped('name')))}
                        for attribute_line in self.attribute_line_ids]

        return {
            'all_prices': all_prices,
            'pricelists': pricelist_list,
            'warehouses': warehouse_list,
            'suppliers': supplier_list,
            'variants': variant_list,
            'locations': locations 
        }



class PosOrder(models.Model):
    _inherit = 'pos.order'


    def _create_picking(self):
        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']
        picking_type = picking_type_obj.search([('code', '=', 'internal')], limit=1)
        
        if not picking_type:
            raise UserError(_('Internal picking type not found.'))

        config_settings = self.env['res.config.settings'].sudo().search([], limit=1)
        location_id = picking_type12.default_location_src_id.id

        for order in self:
            picking_type12 = order.config_id.picking_type_id
            dest_location_id = 55
            print(dest_location_id,"ggggggggggggggggggggggggggggggggggggggggggg")
            existing_picking = picking_obj.search([
                ('picking_type_id', '=', picking_type.id),
                ('location_id', '=', location_id),
                ('location_dest_id', '=', dest_location_id),
                ('state', '!=', 'done')
            ], limit=1)

            if existing_picking:
                for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                    move_vals = {
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': location_id,
                        'location_dest_id': dest_location_id,
                        'picking_id': existing_picking.id,
                    }
                    self.env['stock.move'].create(move_vals)
            else:
                internal_picking_vals = {
                    'picking_type_id': picking_type.id,
                    'location_id': location_id,
                    'location_dest_id': dest_location_id,
                    'move_type': 'direct',
                    'origin': order.name,
                    'move_ids_without_package': [],
                }
                picking = picking_obj.create(internal_picking_vals)
                for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                    move_vals = {
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': location_id,
                        'location_dest_id': dest_location_id,
                        'picking_id': picking.id,
                    }
                    self.env['stock.move'].create(move_vals)

                # Setting the picking to draft status
                picking.state = 'draft'


    @api.model
    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        self._create_picking()
        return res