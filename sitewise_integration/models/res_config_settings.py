import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aws_access_key_id = fields.Char(string='AWS Access Key ID', config_parameter='sitewise_integration.aws_access_key_id')
    aws_secret_access_key = fields.Char(string='AWS Secret Access Key', config_parameter='sitewise_integration.aws_secret_access_key')
    aws_region = fields.Char(string='AWS Region', config_parameter='sitewise_integration.aws_region')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            aws_access_key_id=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id'),
            aws_secret_access_key=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_secret_access_key'),
            aws_region=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_region'),
        )
        _logger.info(f"Get AWS Configurations: {res}")
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_access_key_id', self.aws_access_key_id)
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_secret_access_key', self.aws_secret_access_key)
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_region', self.aws_region)
        _logger.info(f"Set AWS Access Key ID: {self.aws_access_key_id}")
        _logger.info(f"Set AWS Secret Access Key: {self.aws_secret_access_key}")
        _logger.info(f"Set AWS Region: {self.aws_region}")