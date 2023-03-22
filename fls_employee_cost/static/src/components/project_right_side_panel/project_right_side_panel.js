/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { formatFloat } from '@web/views/fields/formatters';
import { session } from '@web/session';
import { ProjectRightSidePanel } from '@project/components/project_right_side_panel/project_right_side_panel';


patch(ProjectRightSidePanel.prototype, "formatMonetary", {
    formatMonetary(value, options = {}) {
        const currency = session.currencies[2];
        const valueFormatted = formatFloat(value, {
            ...options,
            'digits': [false, 0],
            'noSymbol': true,
        });
        if (!currency) {
            return valueFormatted;
        }
        if (currency.position === "after") {
            return `${valueFormatted}\u00A0${currency.symbol}`;
        } else {
            return `${currency.symbol}\u00A0${valueFormatted}`;
        }
    },
    async loadData() {
        if (!this.projectId) { // If this is called from notif, multiples updates but no specific project
            return {};
        }
        const data = await this.orm.call(
            'project.project',
            'get_panel_data',
            [[this.projectId]],
            { context: this.context },
        );
        this.state.data = data;
        // const conversion_rate = await this.orm.call(
        //     'res.currency',
        //     'get_conversion_rate',
        //     [this.projectId, this.state.data.currency_id],
        // );
        // this.conversion_rate = conversion_rate
        return data;
    },
});
