from odoo import models, fields

class MaintenanceAttributeLine(models.Model):
    _name = 'maintenance.attribute.line'
    _description = 'Maintenance Attribute Line'

    attribute_id = fields.Many2one('maintenance.attribute', string='Attribute', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)

class MaintenanceMeasurementLine(models.Model):
    _name = 'maintenance.measurement.line'
    _description = 'Maintenance Measurement Line'

    measurement_id = fields.Many2one('maintenance.measurement', string='Measurement', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)

class MaintenanceTransformLine(models.Model):
    _name = 'maintenance.transform.line'
    _description = 'Maintenance Transform Line'

    transform_id = fields.Many2one('maintenance.transform', string='Transform', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)

class MaintenanceMetricLine(models.Model):
    _name = 'maintenance.metric.line'
    _description = 'Maintenance Metric Line'

    metric_id = fields.Many2one('maintenance.metric', string='Metric', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True)
