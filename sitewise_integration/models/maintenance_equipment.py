import boto3
from odoo import models, fields, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_id', string='Metrics')
    
    aws_access_key_id = ''
    aws_secret_access_key = ''
    aws_region = ''
    
    sitewise_model_id = fields.Char(string='SiteWise Model ID')
    sitewise_asset_id = fields.Char(string='SiteWise Asset ID')

    def get_aws_client(self, service_name):
        return boto3.client(
            service_name,
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def create_sitewise_model(self):
        client = self.get_aws_client('iotsitewise')

        asset_model_payload = {
            "assetModelName": "OdooModel",
            "assetModelDescription": "Model created from Odoo",
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

    def create_sitewise_asset(self):
        client = self.get_aws_client('iotsitewise')

        asset_payload = {
            "assetName": "OdooAsset",
            "assetModelId": self.sitewise_model_id,  # Use the actual asset model ID
            "assetProperties": [
                {
                    "propertyName": "Property1",
                    "value": {
                        "value": {
                            "stringValue": "Value"
                        }
                    }
                }
            ]
        }

        response = client.create_asset(**asset_payload)
        return response

    @api.multi
    def button_create_model(self):
        self.ensure_one()
        response = self.create_sitewise_model()
        if response and 'assetModelId' in response:
            self.sitewise_model_id = response['assetModelId']
        # You can add further logic to handle the response if needed

    @api.multi
    def button_create_asset(self):
        self.ensure_one()
        response = self.create_sitewise_asset()
        if response and 'assetId' in response:
            self.sitewise_asset_id = response['assetId']
        # You can add further logic to handle the response if needed