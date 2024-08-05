from odoo import models, fields, api
import boto3

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aws_access_key_id = fields.Char(string='AWS Access Key ID', config_parameter='sitewise_integration.aws_access_key_id', help='Enter your access key here.')
    aws_secret_access_key = fields.Char(string='AWS Secret Access Key', config_parameter='sitewise_integration.aws_secret_access_key', help='Enter your secret key here.')
    aws_region = fields.Char(string='AWS Region', config_parameter='sitewise_integration.aws_region', help='Enter your region here.')