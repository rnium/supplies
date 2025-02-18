/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useRef, onMounted, useState, useEffect } = owl;
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { StatCard } from "./stat_card/stat_card";
import { Graph } from "./Graph/graph";
import { formatAmount, getDateInterval } from './utils'


export class SuppliesDashboard extends Component {
    setup() {
        this.timeperiods = [
            { tag: 'this_week', label: 'This Week' },
            { tag: 'last_week', label: 'Last Week' },
            { tag: 'last_month', label: 'Last Month' },
            { tag: 'last_year', label: 'Last Year' },
        ];
        this.state = useState({
            suppliers: [],
            selectedSupplierId: "0",
            selectedPeriod: "0",
            productLineIds: [],
            productLines: [],
            rfpPurchaseChartData: null,
            rfqStatusChartData: null,
            another: 'test',
            rfp: {
                'accepted': 0,
                'submitted': 0,
                'total_amount': 0,
            }
        })
        this.orm = useService('orm');

        onWillStart(async () => {
            await this.getSuppliers();
        });

        useEffect(() => {
            this.getRequestForPurchases();
        }, () => [this.state.selectedSupplierId, this.state.selectedPeriod]);

        useEffect(() => {
            if (this.state.productLineIds.length) {
                this.getProductLines();
            }
        }, () => [this.state.productLineIds]);

    }

    async getSuppliers() {
        const suppliers = await this.orm.searchRead('res.partner', [['supplier_rank', '>', 0]], ['name']);
        this.state.suppliers = suppliers;
    }

    async setRfpPurchaseData(accepted_rfps) {
        if (accepted_rfps.length == 0) {
            this.state.rfpPurchaseChartData = null;
            return;
        }
        const data = {
            labels: accepted_rfps.map(r => r.rfp_number),
            datasets: [
                {
                    label: 'Total Amount',
                    data: accepted_rfps.map(r => r.total_amount)
                }
            ]
        }
        this.state.rfpPurchaseChartData = data;
    }

    async setRFQStatusData(rfqs) {
        if (rfqs.length == 0) {
            this.state.rfqStatusChartData = null;
            return;
        }
        const purchase = rfqs.filter(r => r.state === 'purchase').length;
        const draft = rfqs.filter(r => r.state === 'draft').length;
        const cancel = rfqs.filter(r => r.state === 'cancel').length;
        const data = {
            labels: ['Accepted', 'Draft', 'Cancelled'],
            datasets: [
                {
                    label: 'RFQ Status',
                    data: [purchase, draft, cancel]
                }
            ]
        }
        this.state.rfqStatusChartData = data;
    }

    async getRequestForPurchases() {
        const domain = [];
        const rfq_domain = [['rfp_id', '!=', false]];
        if (this.state.selectedSupplierId !== "0") {
            const supplerIdInt = parseInt(this.state.selectedSupplierId);
            domain.push(['approved_supplier_id', '=', supplerIdInt]);
            rfq_domain.push(['partner_id', '=', supplerIdInt]);
        } else {
            return;
        }
        if (this.state.selectedPeriod !== "0") {
            const { start: startDate, end: endDate } = getDateInterval(this.state.selectedPeriod);
            const dateDomains = [['create_date', '>=', startDate], ['create_date', '<=', endDate]];
            domain.push(...dateDomains)
            rfq_domain.push(...dateDomains)
        }
        console.log(domain);
        console.log(rfq_domain);

        const rfps = await this.orm.searchRead('supplies.rfp', domain, ['rfp_number', 'state', 'total_amount', 'product_line_ids']);
        const rfqs = await this.orm.searchRead('purchase.order', rfq_domain, ['state']);
        const accepted_rfps = rfps.filter(r => r.state === 'accepted');
        const submitted = rfqs.length;
        const accepted = accepted_rfps.length;
        let total_amount = accepted_rfps.reduce((acc, r) => acc + r.total_amount, 0);
        if (!isNaN(total_amount) && total_amount > 0) {
            total_amount = formatAmount(total_amount);
        }
        const productLineIds = rfps.map(r => r.product_line_ids).flat();
        this.state.productLineIds = productLineIds;
        this.state.rfp = { accepted, submitted, total_amount };
        await this.setRfpPurchaseData(accepted_rfps);
        await this.setRFQStatusData(rfqs);
    }

    async getProductLines() {
        const productLines = await this.orm.searchRead(
            'supplies.rfp.product.line',
            [['id', 'in', this.state.productLineIds]],
            ['product_name', 'product_qty', 'unit_price', 'delivery_charge', 'subtotal_price', 'product_image']
        );
        this.state.productLines = productLines;
    }
}

SuppliesDashboard.template = 'supplies.dashboard';
SuppliesDashboard.components = { Layout, StatCard, Graph };

registry.category("actions").add("supplies.dashboard", SuppliesDashboard);