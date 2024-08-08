from odoo import models, fields, api


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    sitewise_model_id = fields.Char(string='SiteWise Model ID')

