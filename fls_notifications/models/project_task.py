from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        return # disable notifications for tasks

