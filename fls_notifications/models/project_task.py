from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _task_message_auto_subscribe_notify(self, users_per_task):
        return
