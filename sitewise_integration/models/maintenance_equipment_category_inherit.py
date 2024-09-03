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
        asset_model_properties = []
        # Process maintenance_attribute_line_ids
        for attr_line in self.maintenance_attribute_line_ids:
            asset_model_properties.append({
                "name": attr_line.name.name,
                "dataType": attr_line.data_type.upper(),
                "dataTypeSpec": "STRING",  # Assuming string data type spec for attribute
                "externalId": attr_line.external_id,
                "type": {
                    "attribute": {
                        "defaultValue": attr_line.default_value or ""
                    }
                }
            })
        # Process maintenance_measurement_line_ids
        for measurement_line in self.maintenance_measurement_line_ids:
            asset_model_properties.append({
                "name": measurement_line.name.name,
                "dataType": measurement_line.data_type.upper(),
                "dataTypeSpec": "STRING",  # Assuming string data type spec for measurement
                "externalId": measurement_line.external_id,
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
            })

        # Process maintenance_transform_line_ids
        for transform_line in self.maintenance_transform_line_ids:
            asset_model_properties.append({
                "name": transform_line.name.name,
                "dataType": transform_line.data_type.upper(),
                "dataTypeSpec": "STRING",  # Assuming string data type spec for transform
                "externalId": transform_line.external_id,
                "unit": transform_line.unit or "",
                "type": {
                    "transform": {
                        "expression": transform_line.formula or "",
                        "processingConfig": {
                            "computeLocation": "LOCAL"  # Default compute location; adjust as needed
                        },
                        "forwardingConfig": {
                            "state": "DISABLED"  # Default state; adjust as needed
                        }
                    }
                }
            })
        # Process maintenance_metric_line_ids
        for metric_line in self.maintenance_metric_line_ids:
            asset_model_properties.append({
                "name": metric_line.name.name,
                "dataType": metric_line.data_type.upper(),
                "dataTypeSpec": "STRING",  # Assuming string data type spec for metric
                "externalId": metric_line.external_id,
                "unit": metric_line.unit or "",
                "type": {
                    "metric": {
                        "expression": metric_line.formula or "",
                        "processingConfig": {
                            "computeLocation": "LOCAL"  # Default compute location; adjust as needed
                        },
                        "variables": [],  # Add variables if needed
                        "window": {
                            "tumbling": {
                                "interval": metric_line.time_interval or "1d",  # Default interval
                                "offset": "0"  # Default offset
                            }
                        }
                    }
                }
            })
        # Create the full payload for creating the SiteWise model
        asset_model_payload = {
            "assetModelName": self.name,
            "assetModelDescription": "Model created from Odoo",
            "assetModelProperties": asset_model_properties
        }
        # Send the payload to AWS SiteWise to create the asset model
        response = client.create_asset_model(**asset_model_payload)
        return response


    def button_create_model(self):
        for record in self:
            response = record.create_sitewise_model()
            if response and 'assetModelId' in response:
                record.sitewise_model_id = response['assetModelId']
            # You can add further logic to handle the response if needed


