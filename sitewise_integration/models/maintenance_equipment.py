import boto3
from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError
import time
import re
from html import unescape
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    # Additional fields required for SiteWise integration
    attribute_ids = fields.One2many('maintenance.attribute.line', 'equipment_id', string='Attributes')
    measurement_ids = fields.One2many('maintenance.measurement.line', 'equipment_id', string='Measurements')
    transform_ids = fields.One2many('maintenance.transform.line', 'equipment_id', string='Transforms')
    metric_ids = fields.One2many('maintenance.metric.line', 'equipment_id', string='Metrics')
    # Fields added for IDs fetched from SiteWise
    sitewise_model_id = fields.Char(string='SiteWise Model ID', related='category_id.sitewise_model_id', readonly=True, store=True)
    sitewise_asset_id = fields.Char(string='SiteWise Asset ID', readonly=True,)
    # Fields added for equipment hierarchy
    # parent_id = fields.Many2one('maintenance.equipment', string='Parent Equipment')
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string='Child Equipments')

    @api.onchange('category_id')
    def onchange_data(self):
        _logger.debug("Entering onchange_data function for equipment with category ID: %s", self.category_id.id if self.category_id else 'None')
        if self.category_id:
            self.attribute_ids = self.category_id.maintenance_attribute_line_ids
            self.measurement_ids = self.category_id.maintenance_measurement_line_ids
            self.transform_ids = self.category_id.maintenance_transform_line_ids
            self.metric_ids = self.category_id.maintenance_metric_line_ids
            # self.sitewise_model_id = self.category_id.sitewise_model_id
            # Mapping additional fields from category to equipment
            self.owner_user_id = self.category_id.owner_user_id
            self.maintenance_team_id = self.category_id.maintenance_team_id
            self.technician_user_id = self.category_id.technician_user_id
            self.assign_date = self.category_id.assign_date
            self.scrap_date = self.category_id.scrap_date
            self.location = self.category_id.location
            self.note = self.category_id.note_comment
            self.partner_id = self.category_id.partner_id
            self.partner_ref = self.category_id.partner_ref
            self.model = self.category_id.model
            self.serial_no = self.category_id.serial_no
            self.effective_date = self.category_id.effective_dates
            self.cost = self.category_id.cost
            self.warranty_date = self.category_id.warranty_date
            self.expected_mtbf = self.category_id.expected_mtbf
            self.mtbf = self.category_id.mtbf
            self.estimated_next_failure = self.category_id.estimated_next_failure
            self.latest_failure_date = self.category_id.latest_failure_date
            self.mttr = self.category_id.mttr
            # Load the child equipment based on the child categories of the selected category
            child_categories = self.category_id.child_ids
            if child_categories:
                # Fetch the equipment associated with child categories and map to child_ids
                child_equipments = self.env['maintenance.equipment'].search(
                    [('category_id', 'in', child_categories.ids)])
                self.child_ids = child_equipments
            else:
                self.child_ids = [(5, 0, 0)]  # Clear child_ids if no child categories
        else:
            self.attribute_ids = [(5, 0, 0)]
            self.measurement_ids = [(5, 0, 0)]
            self.transform_ids = [(5, 0, 0)]
            self.metric_ids = [(5, 0, 0)]
            # self.sitewise_model_id = False
        _logger.debug("Exiting onchange_data function")

    # Establishing connection to AWS
    def get_aws_client(self, service_name):
        _logger.debug("Entering get_aws_client function")
        aws_access_key_id = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id')
        aws_secret_access_key = self.env['ir.config_parameter'].sudo().get_param(
            'sitewise_integration.aws_secret_access_key')
        aws_region = self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_region')

        # Add logging to check parameter values
        _logger.info("AWS Access Key ID: %s", aws_access_key_id)
        _logger.info("AWS Secret Access Key: %s", aws_secret_access_key)
        _logger.info("AWS Region: %s", aws_region)

        _logger.debug("Exiting get_aws_client function")
        return boto3.client(
            service_name,
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def _clean_html(self, html_text):
        """Helper method to remove HTML tags and unescape HTML entities."""
        # Remove HTML tags using a regex and then unescape HTML entities
        return unescape(re.sub('<.*?>', '', html_text))

    def create_sitewise_asset(self):
        _logger.debug("Entering create_sitewise_asset function")
        client = self.get_aws_client('iotsitewise')
        # Clean the 'note' field by removing HTML tags and unescaping HTML entities
        asset_description = self._clean_html(self.note) if self.note else ""
        asset_payload = {
            "assetName": self.name,
            "assetModelId": self.category_id.sitewise_model_id,  # Use the actual asset model ID
            "assetDescription": asset_description,
            # "assetDescription": self.note,
        }

        _logger.debug(f"Calling AWS API to create asset with payload: {asset_payload}")
        try:
            response = client.create_asset(**asset_payload)
            _logger.debug(f"AWS response for asset creation: {response}")
            if response and 'assetId' in response:
                self.sitewise_asset_id = response['assetId']
                _logger.info(f"Asset '{self.name}' created in SiteWise with ID: {self.sitewise_asset_id}")
            else:
                raise ValidationError("Failed to create asset in AWS IoT SiteWise.")
        except client.exceptions.ResourceAlreadyExistsException:
            raise ValidationError(f"Asset with name '{self.name}' already exists in AWS IoT SiteWise.")
        except Exception as e:
            _logger.exception("Exception during asset creation")
            raise ValidationError(f"Failed to create asset in AWS IoT SiteWise: {str(e)}")

        _logger.debug("Exiting create_sitewise_asset function")
        return response

    def wait_for_asset_active(self, asset_id, timeout=300, interval=5):
        """
        Wait for the asset to become ACTIVE within the specified timeout.
        """
        _logger.debug(f"Entering wait_for_asset_active function for asset_id: {asset_id}")
        client = self.get_aws_client('iotsitewise')
        elapsed_time = 0

        while elapsed_time < timeout:
            try:
                response = client.describe_asset(assetId=asset_id)
                status = response.get('assetStatus', {}).get('state', '')
                _logger.debug(f"Asset {asset_id} status: {status}")

                if status == 'ACTIVE':
                    _logger.info(f"Asset {asset_id} is ACTIVE")
                    return True
                elif status in ('FAILED', 'DELETING'):
                    raise ValidationError(f"Asset '{asset_id}' is in '{status}' state, which is not valid for operations.")

                time.sleep(interval)
                elapsed_time += interval
            except Exception as e:
                _logger.error(f"Error checking asset status for {asset_id}: {str(e)}")
                raise ValidationError(f"Error checking asset status for {asset_id}: {str(e)}")

        _logger.error(f"Asset '{asset_id}' did not become ACTIVE within the timeout period.")
        raise ValidationError(f"Asset '{asset_id}' did not become ACTIVE within the timeout period.")

    def configure_sitewise_asset(self):
        _logger.debug("Entering configure_sitewise_asset function")
        client = self.get_aws_client('iotsitewise')

        # Update attributes in SiteWise
        for attribute_line in self.attribute_ids:
            if attribute_line.name.external_id:
                try:
                    _logger.debug(f"Updating attribute '{attribute_line.name.name}' in SiteWise")
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
                    _logger.error(f"Failed to update property '{attribute_line.name.name}': {str(e)}")
                    raise ValidationError(f"Failed to update property '{attribute_line.name.name}': {str(e)}")

        # Add Child Assets to the Parent Asset in SiteWise
        for child in self.child_ids:
            if child.sitewise_asset_id:  # Ensure child asset is already created
                # Wait for the child asset to be ACTIVE
                if not self.wait_for_asset_active(child.sitewise_asset_id):
                    raise ValidationError(f"Child asset '{child.name}' is not in ACTIVE state and cannot be associated.")

                hierarchy_id = self.category_id.sitewise_hierarchy_id
                if not hierarchy_id:
                    _logger.error(f"Hierarchy ID not set for category {self.category_id.name} while associating child asset '{child.name}' to parent asset '{self.name}'")
                    raise ValidationError("Hierarchy ID not set for the selected equipment category '{self.category_id.name}'.")

                try:
                    # Log the Hierarchy ID being used
                    _logger.info(f"Associating child asset '{child.name}' using Hierarchy ID: {self.category_id.sitewise_hierarchy_id}")
                    client.associate_assets(
                        assetId=self.sitewise_asset_id,  # Parent asset ID
                        childAssetId=child.sitewise_asset_id,
                        hierarchyId=self.category_id.sitewise_hierarchy_id  # The hierarchy ID of the model

                    )
                except client.exceptions.ResourceNotFoundException:
                    raise ValidationError(f"Child asset '{child.name}' not found in AWS IoT SiteWise.")
                except Exception as e:
                    _logger.error(f"Failed to associate child asset '{child.name}': {str(e)}")
                    raise ValidationError(f"Failed to associate child asset '{child.name}': {str(e)}")

        _logger.debug("Exiting configure_sitewise_asset function")

    def button_create_asset(self):
        _logger.debug("Entering button_create_asset function")
        for record in self:
            # Step 1: Create the Asset in SiteWise
            response = record.create_sitewise_asset()

            # Check if the asset creation was successful
            if response and 'assetId' in response:
                record.sitewise_asset_id = response['assetId']

                # Step 2: Wait for the asset to become ACTIVE
                if not record.wait_for_asset_active(record.sitewise_asset_id):
                    raise ValidationError(f"Asset '{record.name}' did not become ACTIVE in the expected time.")

                # Step 3: Configure the Asset Post-Creation
                record.configure_sitewise_asset()
            else:
                raise ValidationError("Failed to create asset in AWS IoT SiteWise.")
        _logger.debug("Exiting button_create_asset function")
