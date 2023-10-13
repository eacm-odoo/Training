from odoo import api, models, exceptions


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def _check_binary_field_limits(self, vals):
        for field_name, field_value in vals.items():
            field = self._fields.get(field_name)
            if field and field.type == 'binary' and field_value:
                file_size = len(field_value)
                attachment_limit = self.env['ir.config_parameter'].sudo().get_param('fls_attachment.attachment_limit')
                if file_size > float(attachment_limit) * 1024 ** 2:  # convert to bytes
                    raise exceptions.UserError(f"The file size exceeds the maximum limit of {attachment_limit} MB.")

    @api.model
    def create(self, vals):
        self._check_binary_field_limits(vals)
        return super(BaseModel, self).create(vals)

    def write(self, vals):
        self._check_binary_field_limits(vals)
        return super(BaseModel, self).write(vals)
