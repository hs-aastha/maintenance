from odoo import models, fields

class MaintenanceAttribute(models.Model):
    _name = 'maintenance.attribute'
    _description = 'Maintenance Attribute'

    name = fields.Char('Name', required=True)
    default_value = fields.Char('Default Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    #equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
