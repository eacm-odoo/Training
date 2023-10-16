odoo.define('fls_project.project_report', function (require) {
    'use strict';

    var core = require('web.core');
    var account_report = require('account_reports.account_report');

    var projectReportsWidget = account_report.accountReportsWidget.extend({

        filter_search_bar: function(e) {
            var self = this;
            var query = e.target.value.trim().toLowerCase();
            this.filterOn = false;
            const reportLines = this.el.querySelectorAll('.o_account_reports_table tbody tr');
            let lastKnownParent = null;
            let isLastParentHidden = null;
            reportLines.forEach(reportLine => {
                if (reportLine.classList.length == 0) return;
                const lineNameEl = reportLine.querySelector('.account_report_line_name');
                // Only the direct text node, not text situated in other child nodes
                const displayName = lineNameEl.childNodes[0].nodeValue.trim().toLowerCase();
    
                const searchKey = (lineNameEl.dataset.searchKey || '').toLowerCase();
                const name = displayName.replace(searchKey, "");
                let queryFound = undefined;
                if (searchKey) {
                    queryFound = searchKey.includes(query);
                } else {
                    queryFound = displayName.includes(query);
                }
    
                if (reportLine.classList.contains('o_account_searchable_line')){
                    reportLine.classList.toggle('o_account_reports_filtered_lines', !queryFound);
                    lastKnownParent = reportLine.querySelector('.o_account_report_line').dataset.id;
                    isLastParentHidden = !queryFound;
                }
                else if (reportLine.getAttribute('data-parent-id') == lastKnownParent){
                    reportLine.classList.toggle('o_account_reports_filtered_lines', isLastParentHidden);
                }
    
                if (!queryFound) {
                    self.filterOn = true;
                }
            });
    
            // Make sure all ancestors are displayed.
            const $matchingChilds = this.$('tr[data-parent-id]:not(.o_account_reports_filtered_lines):visible');
            $($matchingChilds.get().reverse()).each(function(index, el) {
                const id = $.escapeSelector(String(el.dataset.parentId));
                const $parent = self.$('.o_account_report_line[data-id="' + id + '"]');
                $parent.closest('tr').removeClass('o_account_reports_filtered_lines');
                if ($parent.hasClass('folded')) {
                    $(el).addClass('o_account_reports_filtered_lines');
                }
            });
            if (this.filterOn) {
                this.$('.o_account_reports_level1.total').addClass('o_account_reports_filtered_lines');
            } else {
                this.$('.o_account_reports_level1.total').removeClass('o_account_reports_filtered_lines');
            }
            this.report_options['filter_search_bar'] = query;
            this.render_footnotes();
        },
        order_selected_column: function(e) {
            let self = this;
            if (self.report_options.order_column !== undefined) {
                let colNumber = Array.prototype.indexOf.call(e.currentTarget.parentElement.children, e.currentTarget);
                if (self.report_options.order_column && self.report_options.order_column == colNumber) {
                    self.report_options.order_column = -colNumber;
                } else if (self.report_options.order_column && self.report_options.order_column == -colNumber) {
                    self.report_options.order_column = null;
                } else {
                    self.report_options.order_column = colNumber;
                }
                self.reload();
            }
        },
    });
    core.action_registry.add('project_report', projectReportsWidget);
    return projectReportsWidget
});