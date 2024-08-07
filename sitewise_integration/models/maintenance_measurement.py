from odoo import models, fields

class MaintenanceMeasurement(models.Model):
    _name = 'maintenance.measurement'
    _description = 'Maintenance Measurement'

    name = fields.Char('Name', required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    #equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')