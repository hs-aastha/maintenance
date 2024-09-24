from odoo import models, fields, api

class MaintenanceAttribute(models.Model):
    _name = 'maintenance.attribute'
    _description = 'Maintenance Attribute'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    default_value = fields.Char('Default Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')


class MaintenanceAttributeLine(models.Model):
    _name = 'maintenance.attribute.line'
    _description = 'Maintenance Attribute Line'

    name = fields.Many2one('maintenance.attribute', string="Name", required=True)
    default_value = fields.Char('Default Value')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_attribute_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')

    @api.onchange('name')
    def _onchange_name(self):
        """Automatically fill in the other fields based on the selected 'name'"""
        if self.name:
            self.default_value = self.name.default_value
            self.data_type = self.name.data_type
            self.external_id = self.name.external_id
        else:
            # Clear fields if no name is selected
            self.default_value = False
            self.data_type = False
            self.external_id = False
