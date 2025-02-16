/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useRef, onMounted, useState, useEffect } = owl;
import { useService } from "@web/core/utils/hooks";
import { StatCard } from "./stat_card/stat_card";
import { Layout } from "@web/search/layout";


export class SuppliesDashboard extends Component {
    setup() {
        this.state = useState({
            suppliers: [],
            selectedSupplierId: "0",
            selectedPeriod: "0",
            selectedPeriodDate: null,
            productLineIds: [],
            productLines: [],
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

    async getRequestForPurchases() {
        const domain = [];
        if (this.state.selectedSupplierId !== "0") {
            const supplerIdInt = parseInt(this.state.selectedSupplierId);
            domain.push(['approved_supplier_id', '=', supplerIdInt]);
        } else {
            return;
        }
        if (this.state.selectedPeriod !== "0") {
            const today = new Date();
            const days = parseInt(this.state.selectedPeriod);
            today.setDate(today.getDate() - days);
            const targetDate = today.toISOString().split('T')[0];
            domain.push(['create_date', '>=', targetDate]);
        }

        const rfps = await this.orm.searchRead('supplies.rfp', domain, ['state', 'total_amount', 'product_line_ids']);
        const accepted_rfps = rfps.filter(r => r.state === 'accepted');
        const submitted = rfps.length;
        const accepted = accepted_rfps.length;
        const total_amount = accepted_rfps.reduce((acc, r) => acc + r.total_amount, 0);
        const productLineIds = rfps.map(r => r.product_line_ids).flat();
        this.state.productLineIds = productLineIds;
        this.state.rfp = { accepted, submitted, total_amount };
    }

    async getProductLines() {
        const productLines = await this.orm.searchRead(
            'supplies.rfp.product.line', 
            [['id', 'in', this.state.productLineIds]], 
            ['product_name', 'product_qty', 'unit_price', 'delivery_charge', 'subtotal_price', 'product_image']
        );
        console.log(productLines);
        this.state.productLines = productLines;
    }
}

SuppliesDashboard.template = 'supplies.dashboard';
SuppliesDashboard.components = { Layout, StatCard };

registry.category("actions").add("supplies.dashboard", SuppliesDashboard);