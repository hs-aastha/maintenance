from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_line_ids = fields.One2many('maintenance.attribute.line', 'equipment_id', string='Attributes')
    measurement_line_ids = fields.One2many('maintenance.measurement.line', 'equipment_id', string='Measurements')
    transform_line_ids = fields.One2many('maintenance.transform.line', 'equipment_id', string='Transforms')
    metric_line_ids = fields.One2many('maintenance.metric.line', 'equipment_id', string='Metrics')
