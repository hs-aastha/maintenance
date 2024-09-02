from odoo import models, fields


class MaintenanceMeasurement(models.Model):
    _name = 'maintenance.measurement'
    _description = 'Maintenance Measurement'
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


class MaintenanceMeasurementLine(models.Model):
    _name = 'maintenance.measurement.line'
    _description = 'Maintenance Measurement Line'

    name = fields.Many2one('maintenance.measurement', string="Name", required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_measurement_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment measurement')
