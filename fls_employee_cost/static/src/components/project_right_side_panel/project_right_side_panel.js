/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { formatFloat } from '@web/views/fields/formatters';
import { session } from '@web/session';
import { ProjectRightSidePanel } from '@project/components/project_right_side_panel/project_right_side_panel';

const { onWillStart } = owl;

patch(ProjectRightSidePanel.prototype, "formatMonetary", {
    setup() {
        this._super(...arguments);
        onWillStart(async () => {
            this.conversion_rate = await this.get_conversion_rate();
        });
    },
    formatMonetary(value, options = {}) {
        const currency = session.currencies[2];
        const valueFormatted = formatFloat(value*this.conversion_rate, {
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
    async get_conversion_rate() {
        const conversion_rate = await this.orm.call(
            'res.currency',
            'get_conversion_rate',
            [this.projectId],
        );
        return conversion_rate
    }
});
