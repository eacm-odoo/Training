/** @odoo-module  */
import ListController from 'web.ListController';

var BenchReportListController = ListController.extend({
    buttons_template: 'BenchReport.Buttons',

    // -------------------------------------------------------------------------
    // Public
    // -------------------------------------------------------------------------

    init: function (parent, model, renderer, params) {
        this.context = renderer.state.getContext();
        return this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        if (this.context.no_at_date) {
            this.$buttons.find('button.o_button_at_date').hide();
        }
        this.$buttons.on(
            'click',
            '.o_button_at_date',
            this._onOpenWizard.bind(this)
        );
    },

    // -------------------------------------------------------------------------
    // Handlers
    // -------------------------------------------------------------------------

    /**
     * Handler called when the user clicked on the 'Inventory at Date' button.
     * Opens wizard to display, at choice, the products inventory or a computed
     * inventory at a given date.
     */
    _onOpenWizard: function () {
        var state = this.model.get(this.handle, { raw: true });
        // var stateContext = state.getContext();
        var context = {
            active_model: this.modelName,
        };
        this.do_action({
            res_model: 'hr.bench.report.date',
            views: [[false, 'form']],
            target: 'new',
            type: 'ir.actions.act_window',
            context: context,
        });
    },
});

export default BenchReportListController;
