from odoo import models, fields, api


class MaintenanceTransform(models.Model):
    _name = 'maintenance.transform'
    _description = 'Maintenance Transform'
    _rec_name = "name"

    name = fields.Char('Name', required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('double', 'Double'),
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    formula = fields.Text('Formula')


class MaintenanceTransformLine(models.Model):
    _name = 'maintenance.transform.line'
    _description = 'Maintenance Transform Line'

    name = fields.Many2one('maintenance.transform', string="Name", required=True)
    unit = fields.Char('Unit')
    data_type = fields.Selection([
        ('string', 'String'),
        ('double', 'Double'),
    ], string='Data Type', required=True)
    external_id = fields.Char('External ID')
    formula = fields.Text('Formula')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    maintenance_transform_line_id = fields.Many2one('maintenance.equipment.category', string='Equipment Transform')

    @api.onchange('name')
    def _onchange_name(self):
        """Automatically fill in the other fields based on the selected 'name'"""
        if self.name:
            self.unit = self.name.unit
            self.data_type = self.name.data_type
            self.external_id = self.name.external_id
            self.formula = self.name.formula
        else:
            # Clear fields if no name is selected
            self.unit = False
            self.data_type = False
            self.external_id = False
            self.formula = False
