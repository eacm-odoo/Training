/** @odoo-module */
'use strict';

import ListView from 'web.ListView';
import BenchReportListController from './bench_report_list_controller';
import viewRegistry from 'web.view_registry';

var BenchReportListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: BenchReportListController,
    }),
});

viewRegistry.add('bench_report_list', BenchReportListView);

export default BenchReportListView;
