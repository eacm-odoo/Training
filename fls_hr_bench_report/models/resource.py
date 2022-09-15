from collections import defaultdict
from datetime import timedelta

from odoo import models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    # Identical code to _get_resources_day_total except it uses _work_intervals_batch instead of
    # _attendance_intervals_batch.
    def _get_resources_work_day_total(self, from_datetime, to_datetime, resources=None):
        """
        @return dict with hours of work in each day between `from_datetime` and `to_datetime`
        """
        self.ensure_one()
        resources = self.env['resource.resource'] if not resources else resources
        resources_list = list(resources) + [self.env['resource.resource']]
        # total hours per day:  retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = self._work_intervals_batch(from_full, to_full, resources=resources)

        result = defaultdict(lambda: defaultdict(float))
        for resource in resources_list:
            day_total = result[resource.id]
            if resource.id in intervals:
                for start, stop, meta in intervals[resource.id]:
                    day_total[start.date()] += (stop - start).total_seconds() / 3600
        return result
