function addItem() {
    const container = document.getElementById("items-container");
    
    // Build dropdown options from existing select
    const existingSelect = document.querySelector(".product-select");
    const options = existingSelect ? existingSelect.innerHTML : "";
    
    const newRow = document.createElement("div");
    newRow.className = "item-row";
    newRow.style.display = "flex";
    newRow.style.gap = "10px";
    newRow.style.marginBottom = "10px";
    
    newRow.innerHTML = `
        <select name="item_description[]" class="product-select">
            ${options}
        </select>
        <input type="number" name="item_quantity[]" placeholder="Quantity">
        <input type="number" name="item_price[]" placeholder="Price" readonly>
        <input type="hidden" name="product_id[]">
        <button type="button" onclick="removeItem(this)">❌</button>
    `;
    
    container.appendChild(newRow);
}

function removeItem(button) {
    const row = button.parentElement;
    row.remove();
}
// Auto fill price when product is selected
document.addEventListener("change", function(e) {
    if (e.target.classList.contains("product-select")) {
        const selectedOption = e.target.options[e.target.selectedIndex];
        const price = selectedOption.getAttribute("data-price");
        const productId = selectedOption.getAttribute("data-id");
        
        // Find the price and hidden id inputs in the same row
        const row = e.target.parentElement;
        row.querySelector("input[name='item_price[]']").value = price || "";
        row.querySelector("input[name='product_id[]']").value = productId || "";
    }
});