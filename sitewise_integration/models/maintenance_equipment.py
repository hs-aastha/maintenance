import boto3
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_ids = fields.One2many('maintenance.attribute.line', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement.line', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform.line', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric.line', 'equipment_id', string='Metrics')

    sitewise_model_id = fields.Char(string='SiteWise Model ID', readonly=1)
    sitewise_asset_id = fields.Char(string='SiteWise Asset ID')

    @api.onchange('category_id')
    def onchange_data(self):
        if self.category_id:
            self.attribute_ids = self.category_id.maintenance_attribute_line_ids
            self.measurement_ids = self.category_id.maintenance_measurement_line_ids
            self.transform_ids = self.category_id.maintenance_transform_line_ids
            self.metric_ids = self.category_id.maintenance_metric_line_ids
            self.sitewise_model_id = self._get_sitewise_model_id(self.category_id)
        else:
            self.attribute_ids = [(5, 0, 0)]
            self.measurement_ids = [(5, 0, 0)]
            self.transform_ids = [(5, 0, 0)]
            self.metric_ids = [(5, 0, 0)]

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

    # def create_sitewise_model(self):
    #     client = self.get_aws_client('iotsitewise')
    #
    #     asset_model_payload = {
    #         "assetModelName": "OdooModel",
    #         "assetModelDescription": "Model created from Odoo",
    #         "assetModelProperties": [
    #             {
    #                 "name": "Property1",
    #                 "dataType": "STRING",
    #                 "type": {
    #                     "attribute": {
    #                         "defaultValue": "DefaultValue"
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    #
    #     response = client.create_asset_model(**asset_model_payload)
    #     return response

    def create_sitewise_asset(self):
        client = self.get_aws_client('iotsitewise')

        asset_payload = {
            "assetName": self.name,
            "assetModelId": self.category_id.sitewise_model_id,  # Use the actual asset model ID
            "assetDescription": self.note,
        }

        response = client.create_asset(**asset_payload)
        return response

    # def button_create_model(self):
    #     for record in self:
    #         response = record.create_sitewise_model()
    #         if response and 'assetModelId' in response:
    #             record.sitewise_model_id = response['assetModelId']
    #         # You can add further logic to handle the response if needed

    def button_create_asset(self):
        for record in self:
            response = record.create_sitewise_asset()
            if response and 'assetId' in response:
                record.sitewise_asset_id = response['assetId']
            # You can add further logic to handle the response if needed
