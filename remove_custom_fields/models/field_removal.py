from odoo import api, SUPERUSER_ID

def remove_custom_fields(cr, registry):
    """
    This method removes the fields 'pricelist_item_id' and 'x_product_pricelist_item_id'
    from the product.pricelist.item model.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # الحقول التي سيتم حذفها
    fields_to_remove = [
        'pricelist_item_id',
        'x_product_pricelist_item_id'
    ]
    
    for field_name in fields_to_remove:
        field = env['ir.model.fields'].search([
            ('name', '=', field_name),
            ('model', '=', 'product.pricelist.item')  # التأكد من أن الحقل ينتمي لهذا النموذج
        ])
        if field:
            print(f"Removing field: {field_name} from model product.pricelist.item")
            field.unlink()
