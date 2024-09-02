from odoo import models, fields


class MaintenanceMetric(models.Model):
    _name = 'maintenance.metric'
    _description = 'Maintenance Metric'

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
    time_interval = fields.Selection([
        ('1m', '1 minute'),
        ('5m', '5 minutes'),
        ('15m', '15 minutes'),
        ('1h', '1 hour'),
        ('1d', '1 day'),
        ('1w', '1 week')
    ], string='Time Interval', required=True)
    custom_interval = fields.Char('Custom Interval')


class MaintenanceMetricLine(models.Model):
    _name = 'maintenance.metric.line'
    _description = 'Maintenance Metric Line'

    name = fields.Many2one('maintenance.metric', string="Name", required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    formula = fields.Text('Formula')
    time_interval = fields.Selection([
        ('1m', '1 minute'),
        ('5m', '5 minutes'),
        ('15m', '15 minutes'),
        ('1h', '1 hour'),
        ('1d', '1 day'),
        ('1w', '1 week')
    ], string='Time Interval', required=True)
    custom_interval = fields.Char('Custom Interval')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_metric_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment metric')
