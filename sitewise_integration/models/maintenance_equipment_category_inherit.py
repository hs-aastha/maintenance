from odoo.exceptions import ValidationError
from odoo import models, fields, api
import logging
import boto3
import time

_logger = logging.getLogger(__name__)

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    # Fields added for IDs fetched from Sitewise
    sitewise_model_id = fields.Char(string='SiteWise Model ID')
    # New field for hierarchy ID
    sitewise_hierarchy_id = fields.Char(string='SiteWise Hierarchy ID', readonly=True)

    # Fields added for equipment category hierarchy
    parent_id = fields.Many2one('maintenance.equipment.category', string='Parent Category')
    child_ids = fields.One2many('maintenance.equipment.category', 'parent_id', string='Child Categories')

    # Additional fields required for Sitewise integration
    maintenance_attribute_line_ids = fields.One2many('maintenance.attribute.line', 'maintenance_attribute_line_id', string='Attributes')
    maintenance_measurement_line_ids = fields.One2many('maintenance.measurement.line', 'maintenance_measurement_line_id', string='Measurements')
    maintenance_transform_line_ids = fields.One2many('maintenance.transform.line', 'maintenance_transform_line_id', string='Transforms')
    maintenance_metric_line_ids = fields.One2many('maintenance.metric.line', 'maintenance_metric_line_id', string='Metrics')

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

    def create_sitewise_model(self):
        client = self.get_aws_client('iotsitewise')
        asset_model_properties = []
        asset_model_hierarchies = []

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
                        "variables": [{"name": "variable_name_1"}]  # Update as needed
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
                        "variables": [],  # Add variables if needed
                        "window": {
                            "tumbling": {
                                "interval": metric_line.time_interval or "1d",  # Default interval
                                "offset": "00"
                            }
                        }
                    }
                }
            }
            # Add externalId field if it exists
            if metric_line.external_id:
                property_dict["externalId"] = metric_line.external_id
            asset_model_properties.append(property_dict)

        # Prepare hierarchy information
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
            "assetModelDescription": self.note or ' ',
            "assetModelProperties": asset_model_properties,
            "assetModelHierarchies": asset_model_hierarchies,  # Corrected parameter name
        }

        try:
            # Send the payload to AWS SiteWise to create the asset model
            response = client.create_asset_model(**asset_model_payload)
            self.sitewise_model_id = response['assetModelId']
            # Assuming the first hierarchy is used
            self.sitewise_hierarchy_id = response['assetModelHierarchies'][0]['id']
            return response
        except client.exceptions.ResourceAlreadyExistsException:
            raise ValidationError(f"Asset model with name '{asset_model_payload['assetModelName']}' already exists.")
        except Exception as e:
            raise ValidationError(f"Error creating SiteWise model: {str(e)}")

    def button_create_model(self):
        for record in self:
            response = record.create_sitewise_model()
            if response and 'assetModelId' in response:
                record.sitewise_model_id = response['assetModelId']
            # You can add further logic to handle the response if needed