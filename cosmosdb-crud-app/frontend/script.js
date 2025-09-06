const apiUrl = "/api/ProductFunction";

// Create or Update Product
async function createOrUpdate(action) {
    const product = {
        id: document.getElementById("id").value,
        Name: document.getElementById("name").value,
        Category: document.getElementById("Category").value,
        Price: parseFloat(document.getElementById("price").value)
    };

    const method = action === "create" ? "POST" : "PUT";

    const res = await fetch(apiUrl, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(product)
    });

    document.getElementById("output").innerText = await res.text();
    loadAllProducts();
}

// Read Product by ID and Category
async function readProduct() {
    const id = document.getElementById("readId").value;
    const category = document.getElementById("readCategory").value;
    const res = await fetch(`${apiUrl}?id=${id}&Category=${category}`);
    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}

// Delete Product by ID and Category
async function deleteProduct() {
    const id = document.getElementById("readId").value;
    const category = document.getElementById("readCategory").value;
    const res = await fetch(`${apiUrl}?id=${id}&Category=${category}`, { method: "DELETE" });
    document.getElementById("output").innerText = await res.text();
    loadAllProducts();
}

// Load All Products (Table)
async function loadAllProducts() {
    const res = await fetch(apiUrl);
    let products = [];
    try {
        products = await res.json();
    } catch (e) {
        console.error("Error parsing products:", e);
    }

    const tbody = document.querySelector("#productsTable tbody");
    tbody.innerHTML = "";

    if (Array.isArray(products)) {
        products.forEach(p => {
            const row = `<tr>
                <td>${p.id}</td>
                <td>${p.Name}</td>
                <td>${p.Category}</td>
                <td>${p.Price}</td>
            </tr>`;
            tbody.insertAdjacentHTML("beforeend", row);
        });
    }
}

// Load all products when the page loads
window.onload = loadAllProducts;
