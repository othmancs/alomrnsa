from . import models

def _set_price_before(cr, registry):
    
    sql = """
            UPDATE purchase_order_line
            SET price_before = price_unit
            
        """

    cr.execute(sql)