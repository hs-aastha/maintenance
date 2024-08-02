from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aws_access_key_id = fields.Char(string="AWS Access Key ID")
    aws_secret_access_key = fields.Char(string="AWS Secret Access Key")
    aws_region = fields.Char(string="AWS Region")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            aws_access_key_id=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_access_key_id'),
            aws_secret_access_key=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_secret_access_key'),
            aws_region=self.env['ir.config_parameter'].sudo().get_param('sitewise_integration.aws_region'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_access_key_id', self.aws_access_key_id)
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_secret_access_key', self.aws_secret_access_key)
        self.env['ir.config_parameter'].sudo().set_param('sitewise_integration.aws_region', self.aws_region)
