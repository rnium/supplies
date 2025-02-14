/** @odoo-module */
import { registry } from "@web/core/registry"
const { Component, onWillStart, useRef, onMounted } = owl;

export class SuppliesDashboard extends Component {
    setup() {
    }
}

SuppliesDashboard.template = 'supplies.dashboard';

registry.category("actions").add("supplies.dashboard", SuppliesDashboard);