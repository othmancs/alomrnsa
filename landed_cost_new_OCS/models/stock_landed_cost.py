<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- إضافة خيار تقسيم تكاليف العمران إلى واجهة المستخدم -->
    <record id="view_stock_landed_cost_lines_form_inherit" model="ir.ui.view">
        <field name="name">stock.landed.cost.lines.form.inherit</field>
        <field name="model">stock.landed.cost.lines</field>
        <field name="inherit_id" ref="stock_landed_costs.view_stock_landed_cost_lines_form"/>
        <field name="arch" type="xml">
            <!-- تعديل حقل طريقة التقسيم لإضافة خيار تكاليف العمران -->
            <field name="split_method" position="attributes">
                <attribute name="options">{
                    "no_open": True,
                    "no_create": True,
                    "selection_add": [
                        ["construction_costs", "تكاليف العمران"]
                    ]
                }</attribute>
            </field>
            
            <!-- إظهار حقل النسبة المئوية فقط عند اختيار تكاليف العمران -->
            <field name="percentage" position="attributes">
                <attribute name="attrs">{'invisible': [('split_method', '!=', 'construction_costs')]}</attribute>
                <attribute name="readonly">1</attribute>
            </field>
            
            <!-- إضافة تعليمات للمستخدم -->
            <xpath expr="//field[@name='split_method']" position="after">
                <div class="alert alert-info" attrs="{'invisible': [('split_method', '!=', 'construction_costs')]}">
                    <strong>طريقة حساب تكاليف العمران:</strong><br/>
                    1. يتم حساب النسبة المئوية (إجمالي التكاليف / إجمالي تكلفة الشراء بالريال)<br/>
                    2. يتم تطبيق النسبة على تكلفة كل منتج
                </div>
            </xpath>
        </field>
    </record>
    
    <!-- تعديل عرض قائمة خطوط التكاليف لإظهار النسبة المئوية -->
    <record id="view_stock_landed_cost_lines_tree_inherit" model="ir.ui.view">
        <field name="name">stock.landed.cost.lines.tree.inherit</field>
        <field name="model">stock.landed.cost.lines</field>
        <field name="inherit_id" ref="stock_landed_costs.view_stock_landed_cost_lines_tree"/>
        <field name="arch" type="xml">
            <field name="split_method" position="after">
                <field name="percentage" attrs="{'invisible': [('split_method', '!=', 'construction_costs')]}"/>
            </field>
        </field>
    </record>
</odoo>
