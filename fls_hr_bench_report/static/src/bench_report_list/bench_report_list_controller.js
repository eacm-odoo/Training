/** @odoo-module  */
import { ListController } from "@web/views/list/list_controller";
const { onMounted } = owl ;

class BenchReportListController extends ListController {
    setup(){
        super.setup();
        this.context = this.props.context
        this.$doc = $(document)
        onMounted(() => {
            this.$button = this.$doc[0].querySelector('.o_button_at_date')
            this.renderButtons()
        })
    }
    
    renderButtons() {
        if(this.context.no_at_date){
            this.$button.hide()
        }
        this.$button.addEventListener('click', this._onOpenWizard.bind(this))
    }

    _onOpenWizard() {
        const wizardContext = {
            active_model: this.context.active_model
        };

        this.actionService.doAction({
            res_model: 'hr.bench.report.date',
            views: [[false, 'form']],
            target: 'new',
            type: 'ir.actions.act_window',
            context: wizardContext,
        });
    }
}

export default BenchReportListController;
