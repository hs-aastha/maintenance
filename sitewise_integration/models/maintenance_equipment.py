import boto3
from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    # Additional fields required for SiteWise integration
    attribute_ids = fields.One2many('maintenance.attribute.line', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement.line', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform.line', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric.line', 'equipment_id', string='Metrics')
    # Fields added for IDs fetched from SiteWise
    sitewise_model_id = fields.Char(string='SiteWise Model ID', readonly=True, store=True)
    sitewise_asset_id = fields.Char(string='SiteWise Asset ID')
    # Fields added for equipment hierarchy
    parent_id = fields.Many2one('maintenance.equipment', string='Parent Equipment')
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string='Child Equipments')

    @api.onchange('category_id')
    def onchange_data(self):
        if self.category_id:
            self.attribute_ids = self.category_id.maintenance_attribute_line_ids
            self.measurement_ids = self.category_id.maintenance_measurement_line_ids
            self.transform_ids = self.category_id.maintenance_transform_line_ids
            self.metric_ids = self.category_id.maintenance_metric_line_ids
            self.sitewise_model_id = self.category_id.sitewise_model_id
        else:
            self.attribute_ids = [(5, 0, 0)]
            self.measurement_ids = [(5, 0, 0)]
            self.transform_ids = [(5, 0, 0)]
            self.metric_ids = [(5, 0, 0)]

    # Establishing connection to AWS
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

    def create_sitewise_asset(self):
        client = self.get_aws_client('iotsitewise')

        asset_payload = {
            "assetName": self.name,
            "assetModelId": self.category_id.sitewise_model_id,  # Use the actual asset model ID
            "assetDescription": self.note,
        }

        try:
            response = client.create_asset(**asset_payload)
            return response
        except client.exceptions.ResourceAlreadyExistsException:
            raise ValidationError(f"Asset with name '{self.name}' already exists in AWS IoT SiteWise.")
        except Exception as e:
            raise ValidationError(f"Failed to create asset in AWS IoT SiteWise: {str(e)}")

    def configure_sitewise_asset(self):
        client = self.get_aws_client('iotsitewise')

        # Update attributes in SiteWise
        for attribute_line in self.attribute_ids:
            if attribute_line.name.external_id:
                try:
                    client.update_asset_property(
                        assetId=self.sitewise_asset_id,
                        propertyId=attribute_line.name.external_id,
                        propertyAlias=f"{self.sitewise_asset_id}/{attribute_line.name.name}",
                        propertyValue={
                            'value': {'stringValue': attribute_line.default_value or ""}
                        }
                    )
                except client.exceptions.ResourceNotFoundException:
                    raise ValidationError(f"Property '{attribute_line.name.name}' not found in AWS IoT SiteWise.")
                except Exception as e:
                    raise ValidationError(f"Failed to update property '{attribute_line.name.name}': {str(e)}")

        # Add Child Assets to the Parent Asset in SiteWise
        for child in self.child_ids:
            if child.sitewise_asset_id:  # Ensure child asset is already created
                try:
                    client.associate_assets(
                        assetId=self.sitewise_asset_id,  # Parent asset ID
                        childAssetId=child.sitewise_asset_id,
                        hierarchyId=self.category_id.sitewise_model_id  # The hierarchy ID of the model
                    )
                except client.exceptions.ResourceNotFoundException:
                    raise ValidationError(f"Child asset '{child.name}' not found in AWS IoT SiteWise.")
                except Exception as e:
                    raise ValidationError(f"Failed to associate child asset '{child.name}': {str(e)}")

    def button_create_asset(self):
        for record in self:
            # Step 1: Create the Asset in SiteWise
            response = record.create_sitewise_asset()

            # Check if the asset creation was successful
            if response and 'assetId' in response:
                record.sitewise_asset_id = response['assetId']
                # Step 2: Configure the Asset Post-Creation
                record.configure_sitewise_asset()
            else:
                raise ValidationError("Failed to create asset in AWS IoT SiteWise.")