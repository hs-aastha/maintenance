from odoo import models, fields

class MaintenanceAttribute(models.Model):
    _name = 'maintenance.attribute'
    _description = 'Maintenance Attribute'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    default_value = fields.Char('Default Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')


class MaintenanceAttributeLine(models.Model):
    _name = 'maintenance.attribute.line'
    _description = 'Maintenance Attribute Line'

    name = fields.Many2one('maintenance.attribute', string="Name", required=True)
    default_value = fields.Char('Default Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_attribute_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
