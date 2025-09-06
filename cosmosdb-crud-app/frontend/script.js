const apiUrl = "/api/ProductFunction";

// Create or Update Product
async function createOrUpdate(action) {
    const product = {
        id: document.getElementById("id").value.trim(),
        name: document.getElementById("name").value.trim(),
        Category: document.getElementById("Category").value.trim(),
        price: parseFloat(document.getElementById("price").value)
    };

    const method = action === "create" ? "POST" : "PUT";

    try {
        const res = await fetch(apiUrl, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(product)
        });

        const data = await res.json();
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
        loadAllProducts();
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = err;
    }
}

// Read Product by ID and Category
async function readProduct() {
    const id = document.getElementById("readId").value.trim();
    const category = document.getElementById("readCategory").value.trim();

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`);
        if (!res.ok) throw new Error(await res.text());
        const data = await res.json();
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = err;
    }
}

// Delete Product by ID and Category
async function deleteProduct() {
    const id = document.getElementById("readId").value.trim();
    const category = document.getElementById("readCategory").value.trim();

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`, { method: "DELETE" });
        const data = await res.json();
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
        loadAllProducts();
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = err;
    }
}

// Load All Products (Table)
async function loadAllProducts() {
    try {
        const res = await fetch(apiUrl);
        const products = await res.json();

        const tbody = document.querySelector("#productsTable tbody");
        tbody.innerHTML = "";

        if (Array.isArray(products)) {
            products.forEach(p => {
                const row = `<tr>
                    <td>${p.id}</td>
                    <td>${p.name}</td>
                    <td>${p.Category}</td>
                    <td>${p.price}</td>
                </tr>`;
                tbody.insertAdjacentHTML("beforeend", row);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

// Load all products when the page loads
window.onload = loadAllProducts;






