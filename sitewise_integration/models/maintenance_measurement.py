from odoo import models, fields, api


class MaintenanceMeasurement(models.Model):
    _name = 'maintenance.measurement'
    _description = 'Maintenance Measurement'
    _rec_name = "name"

    name = fields.Char('Name', required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')


class MaintenanceMeasurementLine(models.Model):
    _name = 'maintenance.measurement.line'
    _description = 'Maintenance Measurement Line'

    name = fields.Many2one('maintenance.measurement', string="Name", required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('integer', 'Integer'),
        ('double', 'Double'),
        ('boolean', 'Boolean')
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_measurement_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment measurement')

    @api.onchange('name')
    def _onchange_name(self):
        """Automatically fill in the other fields based on the selected 'name'"""
        if self.name:
            self.unit = self.name.unit
            self.data_type = self.name.data_type
            self.external_id = self.name.external_id
        else:
            # Clear fields if no name is selected
            self.default_value = False
            self.data_type = False
            self.external_id = False
