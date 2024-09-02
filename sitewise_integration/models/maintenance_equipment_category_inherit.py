from odoo import models, fields, api


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    sitewise_model_id = fields.Char(string='SiteWise Model ID')
    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_category_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_category_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_category_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_category_id', string='Metrics')
