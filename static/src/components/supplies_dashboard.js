/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useRef, onMounted, useState, useEffect } = owl;
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { StatCard } from "./stat_card/stat_card";
import { Graph } from "./Graph/graph";


export class SuppliesDashboard extends Component {
    setup() {
        this.timeperiods = [
            {tag: 'this_week', label: 'This Week'},
            {tag: 'last_week', label: 'Last Week'},
            {tag: 'last_month', label: 'Last Month'},
            {tag: 'last_year', label: 'Last Year'},
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

    getDateInterval(interval) {
        const now = new Date();
        let start, end;
    
        switch(interval.toLowerCase()) {
            case 'last_week':
                start = new Date(now);
                start.setDate(now.getDate() - now.getDay() - 7);
                start.setHours(0, 0, 0, 0);
    
                end = new Date(start);
                end.setDate(start.getDate() + 6);
                end.setHours(23, 59, 59, 999);
                break;
    
            case 'this_week':
                start = new Date(now);
                start.setDate(now.getDate() - now.getDay());
                start.setHours(0, 0, 0, 0);
    
                end = new Date(now);
                end.setHours(23, 59, 59, 999);
                break;
    
            case 'last_month':
                start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
                end = new Date(now.getFullYear(), now.getMonth(), 0);
                end.setHours(23, 59, 59, 999);
                break;
    
            case 'last_year':
                start = new Date(now.getFullYear() - 1, 0, 1);
                end = new Date(now.getFullYear() - 1, 11, 31);
                end.setHours(23, 59, 59, 999);
                break;
    
            default:
                throw new Error('Invalid interval specified');
        }
    
        function formatDateLocal(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }
    
        return {
            start: formatDateLocal(start),
            end: formatDateLocal(end)
        };
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
            const { start: startDate, end: endDate } = this.getDateInterval(this.state.selectedPeriod);
            const dateDomains = [['create_date', '>=', startDate], ['create_date', '<=', endDate]];
            domain.push(...dateDomains)
            rfq_domain.push(...dateDomains)
        }

        console.log(domain);
        console.log(rfq_domain);

        const rfps = await this.orm.searchRead('supplies.rfp', domain, ['rfp_number', 'state', 'total_amount', 'product_line_ids']);
        const rfqs = await this.orm.searchRead('purchase.order', rfq_domain, ['name', 'state']);
        const accepted_rfps = rfps.filter(r => r.state === 'accepted');
        const submitted = rfqs.length;
        const accepted = accepted_rfps.length;
        const total_amount = accepted_rfps.reduce((acc, r) => acc + r.total_amount, 0);
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