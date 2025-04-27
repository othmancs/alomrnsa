class MultiBranch(models.Model):
    _name = 'multi.branch'
    _description = 'Branch'
    
    name = fields.Char('Branch Name')
    active = fields.Boolean('Active', default=True)
