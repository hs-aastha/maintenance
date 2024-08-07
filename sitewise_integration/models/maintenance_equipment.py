import boto3
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    attribute_ids = fields.One2many('maintenance.attribute', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric', 'equipment_id', string='Metrics')

    sitewise_model_id = fields.Char(string='SiteWise Model ID', related='equipment_category_id.sitewise_model_id', store=True, readonly=False)
    sitewise_asset_id = fields.Char(string='SiteWise Asset ID')

    def get_aws_client(self, service_name):
        aws_access_key_id = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id')
        aws_secret_access_key = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_secret_access_key')
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

    def create_sitewise_asset(self):
        if not self.sitewise_model_id:
            raise UserError(_("Asset can't be created. There is no existing Sitewise Model for '%s'.") % (self.equipment_category_id.name or ''))

        client = self.get_aws_client('iotsitewise')

        asset_payload = {
            "assetName": "OdooAsset",
            "assetModelId": self.sitewise_model_id,  # Use the actual asset model ID
        }

        response = client.create_asset(**asset_payload)
        return response

    def button_create_asset(self):
        for record in self:
            response = record.create_sitewise_asset()
            if response and 'assetId' in response:
                record.sitewise_asset_id = response['assetId']
            # You can add further logic to handle the response if needed
