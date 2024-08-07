# File: sitewise_integration/models/maintenance_equipment_category.py
from odoo import models, fields, api
import boto3

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    model_name = fields.Char('Model Name')
    model_description = fields.Text('Model Description')
    sitewise_model_id = fields.Char('SiteWise Model ID')

    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_category_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_category_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_category_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_category_id', string='Metrics')

    def get_aws_client(self, service_name):
        aws_access_key_id = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id')
        aws_secret_access_key = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_secret_access_key')
        aws_region = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_region')
        return boto3.client(
            service_name,
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def create_sitewise_model(self):
        client = self.get_aws_client('iotsitewise')
        asset_model_payload = {
            "assetModelName": self.model_name,
            "assetModelDescription": self.model_description,
            "assetModelProperties": [
                {
                    "name": "Property1",
                    "dataType": "STRING",
                    "type": {
                        "attribute": {
                            "defaultValue": "DefaultValue"
                        }
                    }
                }
            ]
        }
        response = client.create_asset_model(**asset_model_payload)
        return response

    def button_create_model(self):
        for record in self:
            response = record.create_sitewise_model()
            if response and 'assetModelId' in response:
                record.sitewise_model_id = response['assetModelId']
            else:
                raise UserError('Failed to create model on AWS SiteWise.')
