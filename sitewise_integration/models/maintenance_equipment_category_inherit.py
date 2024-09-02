from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import boto3


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    sitewise_model_id = fields.Char(string='SiteWise Model ID')
    maintenance_attribute_line_ids = fields.One2many('maintenance.attribute.line', 'maintenance_attribute_line_id', string='Attributes')
    maintenance_measurement_line_ids = fields.One2many('maintenance.measurement.line', 'maintenance_measurement_line_id', string='Measurements')
    maintenance_transform_line_ids = fields.One2many('maintenance.transform.line', 'maintenance_transform_line_id', string='Transforms')
    maintenance_metric_line_ids = fields.One2many('maintenance.metric.line', 'maintenance_metric_line_id', string='Metrics')


    def get_aws_client(self, service_name):
        aws_access_key_id = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id')
        aws_secret_access_key = self.env['ir.config_parameter'].sudo().get_param(
            'sitewise_integration.aws_secret_access_key')
        aws_region = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_region')

        # Add logging to check parameter values
        _logger.info("AWS Access Key ID: %s", aws_access_key_id)
        _logger.info("AWS Secret Access Key: %s", aws_secret_access_key)
        _logger.info("AWS Region: %s", aws_region)

        return boto3.client(
            service_name,
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def create_sitewise_model(self):
        client = self.get_aws_client('iotsitewise')

        asset_model_payload = {
            "assetModelName": self.name,
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


    def button_create_model(self):
        for record in self:
            response = record.create_sitewise_model()
            if response and 'assetModelId' in response:
                record.sitewise_model_id = response['assetModelId']
            # You can add further logic to handle the response if needed


