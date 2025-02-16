/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useRef, onMounted, useState, useEffect } = owl;
import { useService } from "@web/core/utils/hooks";
import { StatCard } from "./stat_card/stat_card";


export class SuppliesDashboard extends Component {
    setup() {
        this.state = useState({
            suppliers: [],
            selectedSupplierId: "0",
            selectedPeriod: "0",
            selectedPeriodDate: null,
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
            targetDate = today.toISOString().split('T')[0];
            domain.push(['create_date', '>=', targetDate]);
        }

        const rfps = await this.orm.searchRead('supplies.rfp', domain, ['state', 'total_amount']);
        const accepted_rfps = rfps.filter(r => r.state === 'accepted');
        const submitted = rfps.length;
        const accepted = accepted_rfps.length;
        const total_amount = accepted_rfps.reduce((acc, r) => acc + r.total_amount, 0);
        this.state.rfp = { accepted, submitted, total_amount };
    }
}

SuppliesDashboard.template = 'supplies.dashboard';
SuppliesDashboard.components = { StatCard };

registry.category("actions").add("supplies.dashboard", SuppliesDashboard);