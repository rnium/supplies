document.addEventListener('DOMContentLoaded', function () {
    function calculateSubtotal(lineId) {
        const quantityEl = document.querySelector(`td[data-line-id='${lineId}']`)
        const priceUnitInput = document.querySelector(`input[name='line-${lineId}-price_unit']`);
        const deliveryChargeInput = document.querySelector(`input[name='line-${lineId}-delivery_charge']`);
        const subtotalSpan = document.querySelector(`.line_subtotal[data-line-id='${lineId}']`);

        if (quantityEl && priceUnitInput && deliveryChargeInput && subtotalSpan) {
            const quantity = parseFloat(quantityEl.textContent) || 0;
            const priceUnit = parseFloat(priceUnitInput.value) || 0;
            const deliveryCharge = parseFloat(deliveryChargeInput.value) || 0;
            const subtotal = (quantity * priceUnit) + deliveryCharge;
            subtotalSpan.textContent = subtotal.toFixed(2);
        }
    }

    document.querySelectorAll('.input_price_unit, .input_delivery_charge').forEach(input => {
        input.addEventListener('input', function () {
            const lineId = this.dataset.lineId;
            calculateSubtotal(lineId);
        });
    });
});
