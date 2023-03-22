from odoo import fields, models, api
from datetime import date
import json


class Project(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one(string='Sales Order', related='sale_line_id.order_id', help="Sales order to which the project is linked.", store=True)
    billed_cost = fields.Float(string="Billed Cost", compute='_compute_profitability', store=True)
    invoiced_revenue = fields.Float(string="Invoiced Revenue", compute='_compute_profitability', store=True)
    current_margin = fields.Float(string="Current Margin", compute='_compute_profitability', store=True)
    current_margin_percentage = fields.Float(string="Current Margin %", compute='_compute_profitability', store=True, group_operator="avg")
    to_bill_cost = fields.Float(string="To Bill Cost", compute='_compute_profitability', store=True)
    to_invoice_revenue = fields.Float(string="To Invoice Revenue", compute='_compute_profitability', store=True)
    future_margin = fields.Float(string="Future Margin", compute='_compute_profitability', store=True)
    future_margin_percentage = fields.Float(string="Future Margin %", compute='_compute_profitability', store=True, group_operator="avg")
    expected_cost = fields.Float(string="Expected Cost", compute='_compute_profitability', store=True)
    expected_revenue = fields.Float(string="Expected Revenue", compute='_compute_profitability', store=True)
    expected_margin = fields.Float(string="Expected Margin", compute='_compute_profitability', store=True)
    expected_margin_percentage = fields.Float(string="Expected Margin %", compute='_compute_profitability', store=True, group_operator="avg")
    
    @api.model
    def get_profitability_conversion_rate(self, projectId):
        origin_currency = self.env['res.currency'].search([('name','=','USD')])
        usd_currency = self.env['res.currency'].search([('name','=','USD')])
        project_id = self.env['project.project'].browse([projectId])
        conversion_rate = self.env['res.currency']._get_conversion_rate(origin_currency,usd_currency,project_id.company_id,date.today().strftime("%m/%d/%y"))

    def _compute_profitability(self):
        for project in self:
            items = project._get_profitability_items()
            from_currency_id = 2
            if project.sale_order_id:
                from_currency_id = project.sale_order_id.pricelist_id.currency_id.id
            usd_conversion_rate = self.env['res.currency'].get_conversion_rate(project.id, from_currency_id)
            project.invoiced_revenue = items['revenues']['total']['invoiced']*usd_conversion_rate
            project.billed_cost = items['costs']['total']['billed']*usd_conversion_rate
            project.current_margin = project.invoiced_revenue + project.billed_cost
            if project.invoiced_revenue == 0 and project.current_margin == 0:
                project.current_margin_percentage = 1
            elif project.invoiced_revenue == 0:
                project.current_margin_percentage = 0
            else:
                project.current_margin / project.invoiced_revenue
            project.to_invoice_revenue = items['revenues']['total']['to_invoice']*usd_conversion_rate
            project.to_bill_cost = items['costs']['total']['to_bill']*usd_conversion_rate
            project.future_margin = project.to_invoice_revenue + project.to_bill_cost
            if project.invoiced_revenue == 0 and project.current_margin == 0:
                project.current_margin_percentage = 1
            elif project.invoiced_revenue == 0:
                project.current_margin_percentage = 0
            else:
                project.current_margin_percentage = project.current_margin / project.invoiced_revenue
            if project.to_invoice_revenue == 0 and project.future_margin == 0:
                project.future_margin_percentage = 1
            elif project.to_invoice_revenue == 0:
                project.future_margin_percentage = 0
            else:
                project.future_margin_percentage = project.future_margin / project.to_invoice_revenue
            project.expected_revenue = project.invoiced_revenue + project.to_invoice_revenue
            project.expected_cost = project.billed_cost + project.to_bill_cost
            project.expected_margin = project.current_margin + project.future_margin
            if project.expected_revenue == 0 and project.expected_margin == 0:
                project.expected_margin_percentage = 1
            elif project.expected_revenue == 0:
                project.expected_margin_percentage = 0
            else:
                project.expected_margin_percentage = project.expected_margin / project.expected_revenue

    def _get_profitability_items_from_aal(self, profitability_items, with_action=True):
        if not self.allow_timesheets:
            total_invoiced = total_to_invoice = 0.0
            revenue_data = []
            for revenue in profitability_items['revenues']['data']:
                if revenue['id'] in ['billable_fixed', 'billable_time', 'billable_milestones', 'billable_manual']:
                    continue
                total_invoiced += revenue['invoiced']
                total_to_invoice += revenue['to_invoice']
                revenue_data.append(revenue)
            profitability_items['revenues'] = {
                'data': revenue_data,
                'total': {'to_invoice': total_to_invoice, 'invoiced': total_invoiced},
            }
            return profitability_items
        aa_line_read_group = self.env['account.analytic.line'].sudo()._read_group(
            self.sudo()._get_profitability_aal_domain(),
            ['timesheet_invoice_type', 'timesheet_invoice_id', 'unit_amount', 'amount', 'ids:array_agg(id)'],
            ['timesheet_invoice_type', 'timesheet_invoice_id'],
            lazy=False)
        can_see_timesheets = with_action and len(self) == 1 and self.user_has_groups('hr_timesheet.group_hr_timesheet_approver')
        revenues_dict = {}
        costs_dict = {}
        total_revenues = {'invoiced': 0.0, 'to_invoice': 0.0}
        total_costs = {'billed': 0.0, 'to_bill': 0.0}
        for res in aa_line_read_group:
            amount = res['amount']
            invoice_type = res['timesheet_invoice_type']
            cost = costs_dict.setdefault(invoice_type, {'billed': 0.0, 'to_bill': 0.0})
            revenue = revenues_dict.setdefault(invoice_type, {'invoiced': 0.0, 'to_invoice': 0.0})
            if amount < 0:  # cost
                cost['billed'] += amount
                total_costs['billed'] += amount
            else:  # revenues
                revenue['invoiced'] += amount
                total_revenues['invoiced'] += amount
            if can_see_timesheets and invoice_type not in ['other_costs', 'other_revenues']:
                cost.setdefault('record_ids', []).extend(res['ids'])
                revenue.setdefault('record_ids', []).extend(res['ids'])

        action_name = None
        if can_see_timesheets:
            action_name = 'action_profitability_items'

        def get_timesheets_action(invoice_type, record_ids):
            args = [invoice_type, [('id', 'in', record_ids)]]
            if len(record_ids) == 1:
                args.append(record_ids[0])
            return {'name': action_name, 'type': 'object', 'args': json.dumps(args)}

        sequence_per_invoice_type = self._get_profitability_sequence_per_invoice_type()

        def convert_dict_into_profitability_data(d, cost=True):
            profitability_data = []
            key1, key2 = ['to_bill', 'billed'] if cost else ['to_invoice', 'invoiced']
            for invoice_type, vals in d.items():
                if not vals[key1] and not vals[key2]:
                    continue
                record_ids = vals.pop('record_ids', [])
                data = {'id': invoice_type, 'sequence': sequence_per_invoice_type[invoice_type], **vals}
                if record_ids:
                    if invoice_type not in ['other_costs', 'other_revenues'] and can_see_timesheets:  # action to see the timesheets
                        action = get_timesheets_action(invoice_type, record_ids)
                        action['context'] = json.dumps({'search_default_groupby_invoice': 1 if not cost and invoice_type == 'billable_time' else 0})
                        data['action'] = action
                profitability_data.append(data)
            return profitability_data

        def merge_profitability_data(a, b):
            return {
                'data': a['data'] + b['data'],
                'total': {key: a['total'][key] + b['total'][key] for key in a['total'].keys() if key in b['total']}
            }

        for revenue in profitability_items['revenues']['data']:
            revenue_id = revenue['id']
            aal_revenue = revenues_dict.pop(revenue_id, {})
            revenue['to_invoice'] += aal_revenue.get('to_invoice', 0.0)
            revenue['invoiced'] += aal_revenue.get('invoiced', 0.0)
            record_ids = aal_revenue.get('record_ids', [])
            if can_see_timesheets and record_ids:
                action = get_timesheets_action(revenue_id, record_ids)
                action['context'] = json.dumps({'search_default_groupby_invoice': 1 if revenue_id == 'billable_time' else 0})
                revenue['action'] = action

        for cost in profitability_items['costs']['data']:
            cost_id = cost['id']
            aal_cost = costs_dict.pop(cost_id, {})
            cost['to_bill'] += aal_cost.get('to_bill', 0.0)
            cost['billed'] += aal_cost.get('billed', 0.0)
            record_ids = aal_cost.get('record_ids', [])
            if can_see_timesheets and record_ids:
                cost['action'] = get_timesheets_action(cost_id, record_ids)

        profitability_items['revenues'] = merge_profitability_data(
            profitability_items['revenues'],
            {'data': convert_dict_into_profitability_data(revenues_dict, False), 'total': total_revenues},
        )
        profitability_items['costs'] = merge_profitability_data(
            profitability_items['costs'],
            {'data': convert_dict_into_profitability_data(costs_dict), 'total': total_costs},
        )
        return profitability_items
        
    def _get_revenues_items_from_sol(self, domain=None, with_action=True):
        ##### CUSTOM CODE START #####
        usd_currency = self.env['res.currency'].search([('name','=','USD')]) 
        sale_line_read_group = self.env['sale.order.line'].sudo()._read_group(
            self._get_profitability_sale_order_items_domain(domain),
            ['product_id', 'ids:array_agg(id)', 'currency_id:array_agg(currency_id)', 'untaxed_amount_to_invoice', 'untaxed_amount_invoiced','invoiced_usd'],
            ['product_id'],
        )
        #####  CUSTOM CODE END  #####
        display_sol_action = with_action and len(self) == 1 and self.user_has_groups('sales_team.group_sale_salesman')
        revenues_dict = {}
        total_to_invoice = total_invoiced = 0.0
        if sale_line_read_group:
            sols_per_product = {}
            ##### CUSTOM CODE START #####
            for res in sale_line_read_group:
                from_currency = self.env['res.currency'].browse([res['currency_id'][0]])
                currency_conversion_rate = self.env['res.currency']._get_conversion_rate(from_currency,usd_currency,self.company_id,date.today().strftime("%m/%d/%y"))
                sols_per_product[res['product_id'][0]] = (
                    res['untaxed_amount_to_invoice']*currency_conversion_rate,
                    res['invoiced_usd'],
                    res['ids'],
                )
            #####  CUSTOM CODE END  #####
            product_read_group = self.env['product.product'].sudo()._read_group(
                [('id', 'in', list(sols_per_product)), ('expense_policy', '=', 'no')],
                ['invoice_policy', 'service_type', 'type', 'ids:array_agg(id)'],
                ['invoice_policy', 'service_type', 'type'],
                lazy=False,
            )
            service_policy_to_invoice_type = self._get_service_policy_to_invoice_type()
            general_to_service_map = self.env['product.template']._get_general_to_service_map()
            for res in product_read_group:
                product_ids = res['ids']
                service_policy = None
                if res['type'] == 'service':
                    service_policy = general_to_service_map.get(
                        (res['invoice_policy'], res['service_type']),
                        'ordered_prepaid')
                for product_id, (amount_to_invoice, amount_invoiced, sol_ids) in sols_per_product.items():
                    if product_id in product_ids:
                        invoice_type = service_policy_to_invoice_type.get(service_policy, 'other_revenues')
                        revenue = revenues_dict.setdefault(invoice_type, {'invoiced': 0.0, 'to_invoice': 0.0})
                        revenue['to_invoice'] += amount_to_invoice
                        total_to_invoice += amount_to_invoice
                        revenue['invoiced'] += amount_invoiced
                        total_invoiced += amount_invoiced
                        if display_sol_action and invoice_type in ['service_revenues', 'other_revenues']:
                            revenue.setdefault('record_ids', []).extend(sol_ids)

            if display_sol_action:
                section_name = 'other_revenues'
                other_revenues = revenues_dict.get(section_name, {})
                sale_order_items = self.env['sale.order.line'] \
                    .browse(other_revenues.pop('record_ids', [])) \
                    ._filter_access_rules_python('read')
                if sale_order_items:
                    if sale_order_items:
                        args = [section_name, [('id', 'in', sale_order_items.ids)]]
                        if len(sale_order_items) == 1:
                            args.append(sale_order_items.id)
                        action_params = {
                            'name': 'action_profitability_items',
                            'type': 'object',
                            'args': json.dumps(args),
                        }
                        other_revenues['action'] = action_params
        sequence_per_invoice_type = self._get_profitability_sequence_per_invoice_type()
        return {
            'data': [{'id': invoice_type, 'sequence': sequence_per_invoice_type[invoice_type], **vals} for invoice_type, vals in revenues_dict.items()],
            'total': {'to_invoice': total_to_invoice, 'invoiced': total_invoiced},
        }

    def _get_revenues_items_from_invoices(self, excluded_move_line_ids=None):
        """
        Get all revenues items from invoices, and put them into their own
        "other_invoice_revenues" section.
        If the final total is 0 for either to_invoice or invoiced (ex: invoice -> credit note),
        we don't output a new section

        :param excluded_move_line_ids a list of 'account.move.line' to ignore
        when fetching the move lines, for example a list of invoices that were
        generated from a sales order
        """
        if excluded_move_line_ids is None:
            excluded_move_line_ids = []
        query = self.env['account.move.line'].sudo()._search([
            ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
            ('parent_state', 'in', ['draft', 'posted']),
            ('price_subtotal', '>', 0),
            ('id', 'not in', excluded_move_line_ids),
        ])
        query.add_where('account_move_line.analytic_distribution ? %s', [str(self.analytic_account_id.id)])
        # account_move_line__move_id is the alias of the joined table account_move in the query
        # we can use it, because of the "move_id.move_type" clause in the domain of the query, which generates the join
        # this is faster than a search_read followed by a browse on the move_id to retrieve the move_type of each account.move.line
        query_string, query_param = query.select('price_subtotal', 'parent_state', 'account_move_line__move_id.move_type', 'account_move_line.currency_id')
        self._cr.execute(query_string, query_param)
        invoices_move_line_read = self._cr.dictfetchall()
        if invoices_move_line_read:
            amount_invoiced = amount_to_invoice = 0.0
            for moves_read in invoices_move_line_read:
                if moves_read['parent_state'] == 'draft':
                    if moves_read['move_type'] == 'out_invoice':
                        amount_to_invoice += moves_read['price_subtotal']
                    else:  # moves_read['move_type'] == 'out_refund'
                        amount_to_invoice -= moves_read['price_subtotal']
                else:  # moves_read['parent_state'] == 'posted'
                    if moves_read['move_type'] == 'out_invoice':
                        amount_invoiced += moves_read['price_subtotal']
                    else:  # moves_read['move_type'] == 'out_refund'
                        amount_invoiced -= moves_read['price_subtotal']
            # don't display the section if the final values are both 0 (invoice -> credit note)
            if amount_invoiced != 0 or amount_to_invoice != 0:
                section_id = 'other_invoice_revenues'
                invoices_revenues = {
                    'id': section_id,
                    'sequence': self._get_profitability_sequence_per_invoice_type()[section_id],
                    'invoiced': amount_invoiced,
                    'to_invoice': amount_to_invoice,
                }
                return {
                    'data': [invoices_revenues],
                    'total': {
                        'invoiced': amount_invoiced,
                        'to_invoice': amount_to_invoice,
                    },
                }
        return {'data': [], 'total': {'invoiced': 0.0, 'to_invoice': 0.0}}
    