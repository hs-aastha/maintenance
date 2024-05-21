from odoo import models, fields

class MaintenanceTransform(models.Model):
    _name = 'maintenance.transform'
    _description = 'Maintenance Transform'

    name = fields.Char('Name', required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    formula = fields.Text('Formula')