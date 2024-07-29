# /path/to/your/addons/sitewise_integration/models/maintenance_equipment.py

from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_id', string='Metrics')
