function addItem() {
    // Get the container where items live
    const container = document.getElementById("items-container");
    
    // Create a new row
    const newRow = document.createElement("div");
    newRow.className = "item-row";
    
    // Add the three inputs to the new row
    newRow.innerHTML = `
        <input type="text" name="item_description[]" placeholder="Enter item description">
        <input type="number" name="item_quantity[]" placeholder="Enter quantity">
        <input type="number" name="item_price[]" placeholder="Enter price" step="0.01">
    `;
    
    // Add the new row to the container
    container.appendChild(newRow);
}