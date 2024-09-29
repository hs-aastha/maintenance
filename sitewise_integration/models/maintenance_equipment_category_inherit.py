from odoo.exceptions import ValidationError
from odoo import models, fields, api
import logging
import boto3
import time
from datetime import datetime, date

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all log levels


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    # Fields added for IDs fetched from Sitewise
    sitewise_model_id = fields.Char(string='SiteWise Model ID', readonly=True)
    # New field for hierarchy ID
    sitewise_hierarchy_id = fields.Char(string='SiteWise Hierarchy ID', readonly=True)

    # Fields added for equipment category hierarchy
    parent_id = fields.Many2one('maintenance.equipment.category', string='Parent Category')
    child_ids = fields.One2many('maintenance.equipment.category', 'parent_id', string='Child Categories')

    # Additional fields required for Sitewise integration
    maintenance_attribute_line_ids = fields.One2many('maintenance.attribute.line', 'maintenance_attribute_line_id',
                                                     string='Attributes')
    maintenance_measurement_line_ids = fields.One2many('maintenance.measurement.line',
                                                       'maintenance_measurement_line_id', string='Measurements')
    maintenance_transform_line_ids = fields.One2many('maintenance.transform.line', 'maintenance_transform_line_id',
                                                     string='Transforms')
    maintenance_metric_line_ids = fields.One2many('maintenance.metric.line', 'maintenance_metric_line_id',
                                                  string='Metrics')

    # Add fields same as equipment
    owner_user_id = fields.Many2one('res.users', string="Owner")
    maintenance_team_id = fields.Many2one('maintenance.team', string="Maintenance Team")
    technician_user_id = fields.Many2one('res.users', string="Technician")
    assign_date = fields.Date(string="Assigned Date")
    scrap_date = fields.Date(string="Scrap Date")
    location = fields.Char(string="Location")
    note_comment = fields.Text()
    partner_id = fields.Many2one('res.partner', string="Vendor")
    partner_ref = fields.Char(string="Vendor Reference")
    model = fields.Char(string="Model")
    serial_no = fields.Char(string="Serial Number")
    effective_dates = fields.Date(string="Effective Date")
    cost = fields.Float(string="Cost")
    warranty_date = fields.Date(string="Warranty Expiration Date")
    expected_mtbf = fields.Integer(string="Expected Mean Time Between Failure")
    mtbf = fields.Integer(string="Mean Time Between Failure")
    estimated_next_failure = fields.Date(string="Estimated Next Failure")
    latest_failure_date = fields.Date(string="Latest Failure")
    mttr = fields.Integer(string="Mean Time To Repair")

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

    def wait_for_model_active(self, asset_model_id, timeout=300, interval=5):
        """
        Wait for the asset model to become ACTIVE.
        """
        _logger.debug(f"Waiting for asset model {asset_model_id} to become ACTIVE")
        client = self.get_aws_client('iotsitewise')
        elapsed_time = 0

        while elapsed_time < timeout:
            try:
                response = client.describe_asset_model(assetModelId=asset_model_id)
                # New logging statement for full response
                _logger.debug(f"Full response from describe_asset_model: {response}")
                status = response.get('assetModelStatus', {}).get('state', '')
                _logger.debug(f"Model {asset_model_id} status: {status}")

                if status == 'ACTIVE':
                    _logger.info(f"Asset model {asset_model_id} is ACTIVE")
                    return response
                elif status in ('FAILED', 'DELETING'):
                    raise ValidationError(f"Asset model '{asset_model_id}' is in '{status}' state and cannot be used.")

                time.sleep(interval)
                elapsed_time += interval
            except Exception as e:
                _logger.error(f"Error checking asset model status for {asset_model_id}: {str(e)}")
                raise ValidationError(f"Error checking asset model status for {asset_model_id}: {str(e)}")

        _logger.error(f"Asset model '{asset_model_id}' did not become ACTIVE within the timeout period.")
        raise ValidationError(f"Asset model '{asset_model_id}' did not become ACTIVE within the timeout period.")

    def create_sitewise_model(self):
        _logger.debug("Entering create_sitewise_model function")
        client = self.get_aws_client('iotsitewise')
        asset_model_properties = []
        asset_model_hierarchies = []
        property_name_to_id = ''
        # Prepare asset model properties
        # Process maintenance_attribute_line_ids
        for attr_line in self.maintenance_attribute_line_ids:
            property_dict = {
                "name": attr_line.name.name,
                "dataType": attr_line.data_type.upper(),
                "type": {
                    "attribute": {
                        "defaultValue": attr_line.default_value or ""
                    }
                }
            }
            # Add externalId field if it exists
            if attr_line.external_id:
                property_dict["externalId"] = attr_line.external_id
            asset_model_properties.append(property_dict)

        # Process maintenance_measurement_line_ids
        for measurement_line in self.maintenance_measurement_line_ids:
            if measurement_line.data_type.upper() not in ['DOUBLE', 'INTEGER']:
                raise ValidationError(
                    f"Invalid data type '{measurement_line.data_type}' for measurement '{measurement_line.name.name}'. Must be 'DOUBLE' or 'INTEGER'.")
            property_dict = {
                "name": measurement_line.name.name,
                "dataType": measurement_line.data_type.upper(),
                "unit": measurement_line.unit or "",
                "type": {
                    "measurement": {
                        "processingConfig": {
                            "forwardingConfig": {
                                "state": "DISABLED"  # Default state; adjust as needed
                            }
                        }
                    }
                }
            }
            # Add externalId field if it exists
            if measurement_line.external_id:
                property_dict["externalId"] = measurement_line.external_id
            asset_model_properties.append(property_dict)
            property_name_to_id = measurement_line.name.name
        # Process maintenance_transform_line_ids
        for transform_line in self.maintenance_transform_line_ids:
            if transform_line.data_type.upper() not in ['DOUBLE', 'STRING']:
                raise ValidationError(
                    f"Invalid data type '{transform_line.data_type}' for transform '{transform_line.name.name}'. Must be 'DOUBLE' or 'STRING'.")
            property_dict = {
                "name": transform_line.name.name,
                "dataType": transform_line.data_type.upper(),
                "unit": transform_line.unit or "",
                "type": {
                    "transform": {
                        "expression": transform_line.formula or "",
                        "processingConfig": {
                            "computeLocation": "EDGE",  # Default location; adjust as needed
                            "forwardingConfig": {
                                "state": "DISABLED"  # Default state; adjust as needed
                            }
                        },
                        "variables": [
                            {
                                "name": "torque",
                                "value": {
                                    "propertyId": property_name_to_id
                                }
                            }
                        ]
                    }
                }
            }
            # Add externalId field if it exists
            if transform_line.external_id:
                property_dict["externalId"] = transform_line.external_id
            asset_model_properties.append(property_dict)
        # Process maintenance_metric_line_ids
        for metric_line in self.maintenance_metric_line_ids:
            if metric_line.data_type.upper() not in ['DOUBLE', 'STRING']:
                raise ValidationError(
                    f"Invalid data type '{metric_line.data_type}' for metric '{metric_line.name.name}'. Must be 'DOUBLE' or 'STRING'.")
            property_dict = {
                "name": metric_line.name.name,
                "dataType": metric_line.data_type.upper(),
                "unit": metric_line.unit or "",
                "type": {
                    "metric": {
                        "expression": metric_line.formula or "",
                        "processingConfig": {
                            "computeLocation": "EDGE"  # Default location; adjust as needed
                        },
                        "variables": [
                            {
                                "name": "torque",
                                "value": {
                                    "propertyId": property_name_to_id
                                }
                            },
                        ],
                        "window": {
                            "tumbling": {
                                "interval": metric_line.time_interval or "1d",  # Default interval
                                # "offset": "00"
                            }
                        }
                    }
                }
            }
            # Add externalId field if it exists
            if metric_line.external_id:
                property_dict["externalId"] = metric_line.external_id
            asset_model_properties.append(property_dict)
        # Include technician_user_id in the asset model properties
        if self.technician_user_id:
            asset_model_properties.append(
                self.create_property("Technician", "STRING", default_value=self.technician_user_id.name))
        if self.owner_user_id:
            asset_model_properties.append(
                self.create_property("Owner", "STRING", default_value=self.owner_user_id.name))
        if self.maintenance_team_id:
            asset_model_properties.append(
                self.create_property("Maintenance Team", "STRING", default_value=self.maintenance_team_id.name))
        if self.assign_date:
            asset_model_properties.append(
                self.create_property("Assigned Date", "STRING", default_value=self.assign_date))
        if self.scrap_date:
            asset_model_properties.append(self.create_property("Scrap Date", "STRING", default_value=self.scrap_date))
        if self.location:
            asset_model_properties.append(self.create_property("Location", "STRING", default_value=self.location))
        if self.note:
            asset_model_properties.append(self.create_property("Comments", "STRING", default_value=self.note))
        if self.partner_id:
            asset_model_properties.append(self.create_property("Vendor", "STRING", default_value=self.partner_id.name))
        if self.partner_ref:
            asset_model_properties.append(
                self.create_property("Vendor Reference", "STRING", default_value=self.partner_ref))
        if self.model:
            asset_model_properties.append(self.create_property("Model", "STRING", default_value=self.model))
        if self.serial_no:
            asset_model_properties.append(self.create_property("Serial Number", "STRING", default_value=self.serial_no))
        if self.effective_dates:
            asset_model_properties.append(
                self.create_property("Effective Date", "STRING", default_value=self.effective_dates))
        if self.cost:
            asset_model_properties.append(self.create_property("Cost", "DOUBLE", default_value=self.cost))
        if self.warranty_date:
            asset_model_properties.append(
                self.create_property("Warranty Expiration Date", "STRING", default_value=self.warranty_date))
        if self.alias_name:
            asset_model_properties.append(self.create_property("Email Alias", "STRING", default_value=self.alias_name))
        # Prepare hierarchy information
        if not self.child_ids:
            _logger.info(f"No child categories found for {self.name}. Proceeding without hierarchies.")
        else:
            for child in self.child_ids:
                if not child.sitewise_model_id:  # Ensure child has a valid SiteWise Model ID
                    raise ValidationError(
                        f"Child Category '{child.name}' does not have an associated SiteWise Model. Please create the model first."
                    )
                hierarchy_dict = {
                    "name": child.name,
                    "childAssetModelId": child.sitewise_model_id,
                }
                asset_model_hierarchies.append(hierarchy_dict)

        # Create the full payload for creating the SiteWise model
        asset_model_payload = {
            "assetModelName": self.name,
            "assetModelDescription": self.note_comment or ' ',
            "assetModelProperties": asset_model_properties,
            "assetModelHierarchies": asset_model_hierarchies,
        }

        _logger.debug(f"Calling AWS API to create asset model with payload: {asset_model_payload}")
        # test code
        if self.sitewise_model_id:
            _logger.debug(f"Updating existing SiteWise model with ID: {self.sitewise_model_id}")
            asset_model_payload = {
                "assetModelId": self.sitewise_model_id,
                "assetModelName": self.name,
                "assetModelDescription": self.note_comment or ' ',
                "assetModelProperties": asset_model_properties,
                "assetModelHierarchies": asset_model_hierarchies,
            }
            try:
                response = client.update_asset_model(**asset_model_payload)
                _logger.debug(f"AWS response for model update: {response}")
            except Exception as e:
                _logger.error(f"Error updating SiteWise model: {str(e)}")
                raise ValidationError(f"Error updating SiteWise model: {str(e)}")
        else:
            try:
                # Send the payload to AWS SiteWise to create the asset model
                response = client.create_asset_model(**asset_model_payload)
                _logger.debug(f"AWS response for model creation: {response}")
                self.sitewise_model_id = response['assetModelId']

                # Wait for the model to become ACTIVE
                model_details = self.wait_for_model_active(self.sitewise_model_id)

                # Check for hierarchies only if child_ids exist
                hierarchies = model_details.get('assetModelHierarchies', [])
                if self.child_ids and not hierarchies:
                    _logger.error(f"No hierarchies found in the asset model: {model_details}")
                    raise ValidationError("No hierarchies found in the asset model.")
                else:
                    for hierarchy in hierarchies:
                        _logger.info(f"Stored Hierarchy ID for {self.name}: {hierarchy['id']}")
                        self.sitewise_hierarchy_id = hierarchy['id']

                _logger.debug("Exiting create_sitewise_model function")
                return response
            except client.exceptions.ResourceAlreadyExistsException:
                raise ValidationError(
                    f"Asset model with name '{asset_model_payload['assetModelName']}' already exists.")
            except Exception as e:
                _logger.error(f"Error creating SiteWise model: {str(e)}")
                raise ValidationError(f"Error creating SiteWise model: {str(e)}")


def create_property(self, name, data_type, default_value="", external_id=None):
    """Helper to create a generic property."""
    if isinstance(default_value, (date, datetime)):
        default_value = default_value.strftime("%Y-%m-%d")  # Format date as a string
    elif isinstance(default_value, float):
        default_value = str(default_value)  # Convert float to string
    property_dict = {
        "name": name,
        "dataType": data_type,
        "type": {
            "attribute": {
                "defaultValue": default_value
            }
        }
    }
    if external_id:
        property_dict["externalId"] = external_id
    return property_dict


def button_create_model(self):
    _logger.debug("Entering button_create_model function")
    for record in self:
        response = record.create_sitewise_model()
        if response and 'assetModelId' in response:
            record.sitewise_model_id = response['assetModelId']
    _logger.debug("Exiting button_create_model function")
    # You can add further logic to handle the response if needed
