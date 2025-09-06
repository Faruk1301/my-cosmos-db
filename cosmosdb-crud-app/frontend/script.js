const apiUrl = "/api/ProductFunction";

// Create or Update Product
async function createOrUpdate(action) {
    const product = {
        id: document.getElementById("id").value,
        name: document.getElementById("name").value,
        Category: document.getElementById("Category").value,
        price: parseFloat(document.getElementById("price").value)
    };

    const method = action === "create" ? "POST" : "PUT";

    try {
        const res = await fetch(apiUrl, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(product)
        });

        let data;
        try {
            data = await res.json();
        } catch {
            data = { message: await res.text() };
        }

        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
        loadAllProducts();
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = err;
    }
}

// Read Product by ID and Category
async function readProduct() {
    const id = document.getElementById("readId").value;
    const category = document.getElementById("readCategory").value;

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`);
        let data;
        try {
            data = await res.json();
        } catch {
            data = { message: await res.text() };
        }

        document.getElementById("output").innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        console.error(err);
        document.getElementById("output").innerText = err;
    }
}

// Delete Product by ID and Category
async function deleteProduct() {
    const id = document.getElementById("readId").value;
    const category = document.getElementById("readCategory").value;

    try {
        const res = await fetch(`${apiUrl}?id=${encodeURIComponent(id)}&Category=${encodeURIComponent(category)}`, { method: "DELETE" });
        let data;
        try {
            data = await res.json();
        } catch {
            data = { message: await res.text() };
        }

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
                    <td>${p.name}</td>
                    <td>${p.Category}</td>
                    <td>${p.price}</td>
                </tr>`;
                tbody.insertAdjacentHTML("beforeend", row);
            });
        }
    } catch (err) {
        console.error("Load error:", err);
    }
}

// Load all products when the page loads
window.onload = loadAllProducts;




