const apiUrl = "/api/ProductFunction";

// Helper to trim input values
function getInputValue(id) {
    const el = document.getElementById(id);
    return el ? el.value.trim() : "";
}

// Create or Update Product
async function createOrUpdate(action) {
    const product = {
        id: getInputValue("id"),
        name: getInputValue("name"),
        Category: getInputValue("Category"),
        price: parseFloat(getInputValue("price")) || 0
    };

    if (!product.id || !product.Category) {
        document.getElementById("output").innerText = "ID and Category are required!";
        return;
    }

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
        document.getElementById("output").innerText = "Error: " + err;
    }
}

// Read Product by ID and Category
async function readProduct() {
    const id = getInputValue("readId");
    const category = getInputValue("readCategory");

    if (!id || !category) {
        document.getElementById("output").innerText = "ID and Category are required!";
        return;
    }

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`);
        const data = await res.json();
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = "Error: " + err;
    }
}

// Delete Product by ID and Category
async function deleteProduct() {
    const id = getInputValue("readId");
    const category = getInputValue("readCategory");

    if (!id || !category) {
        document.getElementById("output").innerText = "ID and Category are required!";
        return;
    }

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`, { method: "DELETE" });
        const data = await res.json();
        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
        loadAllProducts();
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = "Error: " + err;
    }
}

// Load All Products into Table
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

// Load all products on page load
window.onload = loadAllProducts;


