from odoo import models, fields


class MaintenanceTransform(models.Model):
    _name = 'maintenance.transform'
    _description = 'Maintenance Transform'
    _rec_name = "name"

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


class MaintenanceTransformLine(models.Model):
    _name = 'maintenance.transform.line'
    _description = 'Maintenance Transform Line'

    name = fields.Many2one('maintenance.transform', string="Name", required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    formula = fields.Text('Formula')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_transform_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment Transform')
