from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_id', string='Metrics')

    def action_create_model(self):
        # Placeholder method for 'Create Model' button
        # Add your functionality here
        return

    def action_create_asset(self):
        # Placeholder method for 'Create Asset' button
        # Add your functionality here
        return