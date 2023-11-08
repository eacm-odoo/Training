/** @odoo-module */

import { listView } from '@web/views/list/list_view';
import { registry } from '@web/core/registry';

import BenchReportListController  from './bench_report_list_controller';

export const BenchReportListView = {
    ...listView,
    buttonTemplate: 'BenchReport.Buttons',
    Controller: BenchReportListController,
    props() {
        const props = listView.props(...arguments);
        props.showButtons = true;
        return props;
    },
}

registry.category('views').add('bench_report_list', BenchReportListView);

export default BenchReportListView;
