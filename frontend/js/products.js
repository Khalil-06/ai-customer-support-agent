let products = [];

let editingProductId = null;

let deletingProductId = null;


document.addEventListener(
    "DOMContentLoaded",
    () => {

        checkAuthentication();

        loadUser();

        loadProducts();

        setupEvents();

    }
);


function checkAuthentication() {

    const token =
        localStorage.getItem("access_token");

    if (!token) {

        window.location.href =
            "login.html";

    }

}


function loadUser() {

    const storedUser =
        localStorage.getItem("user");

    if (!storedUser) {
        return;
    }

    const user =
        JSON.parse(storedUser);

    const email =
        user.email || "User";

    const name =
        email.split("@")[0];

    document.getElementById(
        "userName"
    ).textContent = name;

    document.getElementById(
        "userRole"
    ).textContent =
        user.role || "User";

    document.getElementById(
        "workspaceName"
    ).textContent = name;

    const initial =
        name.charAt(0).toUpperCase();

    document.getElementById(
        "userAvatar"
    ).textContent = initial;

    document.getElementById(
        "workspaceAvatar"
    ).textContent = initial;

}


async function loadProducts() {

    const tableBody =
        document.getElementById(
            "productTableBody"
        );

    tableBody.innerHTML = `
        <tr>
            <td colspan="4" class="loading-cell">
                Loading products...
            </td>
        </tr>
    `;


    try {

        const data =
            await apiRequest("/products");


        products =
            Array.isArray(data)
                ? data
                : data.products || [];


        document.getElementById(
            "productCount"
        ).textContent =
            products.length;


        renderProducts(products);


    } catch (error) {

        tableBody.innerHTML = "";

        showProductMessage(
            error.message,
            true
        );

    }

}


function renderProducts(list) {

    const tableBody =
        document.getElementById(
            "productTableBody"
        );

    const emptyState =
        document.getElementById(
            "emptyProducts"
        );


    if (!list.length) {

        tableBody.innerHTML = "";

        emptyState.style.display =
            "block";

        return;

    }


    emptyState.style.display =
        "none";


    tableBody.innerHTML =
        list.map(product => {

            const initial =
                String(product.name || "P")
                    .charAt(0)
                    .toUpperCase();


            return `

                <tr>

                    <td>

                        <div class="product-name">

                            <div class="product-avatar">
                                ${initial}
                            </div>

                            <div>

                                <strong>
                                    ${escapeHtml(
                                        product.name
                                    )}
                                </strong>

                                <span>
                                    Catalog product
                                </span>

                            </div>

                        </div>

                    </td>


                    <td>

                        <span class="product-id">
                            #${product.product_id}
                        </span>

                    </td>


                    <td>

                        <strong class="product-price">
                            ${formatPrice(
                                product.price
                            )}
                        </strong>

                    </td>


                    <td>

                        <div class="product-actions">

                            <button
                                class="edit-product"
                                onclick="editProduct(
                                    ${product.product_id}
                                )"
                            >
                                Edit
                            </button>

                            <button
                                class="delete-product"
                                onclick="openDeleteModal(
                                    ${product.product_id}
                                )"
                            >
                                Delete
                            </button>

                        </div>

                    </td>

                </tr>

            `;

        }).join("");

}


function setupEvents() {

    document.getElementById(
        "productSearch"
    ).addEventListener(
        "input",
        searchProducts
    );


    document.getElementById(
        "openProductModal"
    ).addEventListener(
        "click",
        () => openProductModal()
    );


    document.getElementById(
        "closeProductModal"
    ).addEventListener(
        "click",
        closeProductModal
    );


    document.getElementById(
        "cancelProduct"
    ).addEventListener(
        "click",
        closeProductModal
    );


    document.getElementById(
        "productForm"
    ).addEventListener(
        "submit",
        saveProduct
    );


    document.getElementById(
        "cancelDelete"
    ).addEventListener(
        "click",
        closeDeleteModal
    );


    document.getElementById(
        "confirmDelete"
    ).addEventListener(
        "click",
        deleteProduct
    );


    document.getElementById(
        "logoutButton"
    ).addEventListener(
        "click",
        logout
    );


    document.getElementById(
        "productModal"
    ).addEventListener(
        "click",
        function(event) {

            if (event.target === this) {
                closeProductModal();
            }

        }
    );


    document.getElementById(
        "deleteModal"
    ).addEventListener(
        "click",
        function(event) {

            if (event.target === this) {
                closeDeleteModal();
            }

        }
    );

}


function searchProducts(event) {

    const query =
        event.target.value
            .toLowerCase()
            .trim();


    if (!query) {

        renderProducts(products);

        return;

    }


    const filtered =
        products.filter(product =>

            String(product.product_id)
                .includes(query)

            ||

            String(product.name)
                .toLowerCase()
                .includes(query)

        );


    renderProducts(filtered);

}


function openProductModal(product = null) {

    const modal =
        document.getElementById(
            "productModal"
        );

    const title =
        document.getElementById(
            "productModalTitle"
        );

    const saveButton =
        document.getElementById(
            "saveProduct"
        );


    document.getElementById(
        "productFormMessage"
    ).textContent = "";


    if (product) {

        editingProductId =
            product.product_id;

        title.textContent =
            "Edit product";

        saveButton.textContent =
            "Save changes";


        document.getElementById(
            "productId"
        ).value =
            product.product_id;


        document.getElementById(
            "productId"
        ).disabled = true;


        document.getElementById(
            "productName"
        ).value =
            product.name;


        document.getElementById(
            "productPrice"
        ).value =
            product.price;


    } else {

        editingProductId = null;

        title.textContent =
            "Add product";

        saveButton.textContent =
            "Add product";


        document.getElementById(
            "productForm"
        ).reset();


        document.getElementById(
            "productId"
        ).disabled = false;

    }


    modal.classList.add("show");

}


function closeProductModal() {

    document.getElementById(
        "productModal"
    ).classList.remove("show");


    document.getElementById(
        "productForm"
    ).reset();


    document.getElementById(
        "productId"
    ).disabled = false;


    editingProductId = null;

}
function openProductModal(product = null) {

    const modal =
        document.getElementById("productModal");

    const title =
        document.getElementById("productModalTitle");

    const saveButton =
        document.getElementById("saveProduct");

    document.getElementById(
        "productFormMessage"
    ).textContent = "";


    if (product) {

        editingProductId =
            product.product_id;

        title.textContent =
            "Edit product";

        saveButton.textContent =
            "Save changes";

        document.getElementById(
            "productId"
        ).value =
            product.product_id;

        document.getElementById(
            "productId"
        ).disabled = true;

        document.getElementById(
            "productName"
        ).value =
            product.name;

        document.getElementById(
            "productPrice"
        ).value =
            product.price;

    } else {

        editingProductId = null;

        title.textContent =
            "Add product";

        saveButton.textContent =
            "Add product";

        document.getElementById(
            "productForm"
        ).reset();

        document.getElementById(
            "productId"
        ).disabled = false;
    }


    modal.classList.add("show");
}

function editProduct(productId) {

    const product =
        products.find(
            item =>
                Number(item.product_id) ===
                Number(productId)
        );


    if (!product) {
        return;
    }


    openProductModal(product);

}


async function saveProduct(event) {

    event.preventDefault();


    const button =
        document.getElementById(
            "saveProduct"
        );

    const message =
        document.getElementById(
            "productFormMessage"
        );


    const productId =
        Number(
            document.getElementById(
                "productId"
            ).value
        );


    const name =
        document.getElementById(
            "productName"
        ).value.trim();


    const price =
        Number(
            document.getElementById(
                "productPrice"
            ).value
        );


    if (!name) {

        message.textContent =
            "Product name is required.";

        return;

    }


    if (!Number.isFinite(price) || price < 0) {

        message.textContent =
            "Enter a valid price.";

        return;

    }


    button.disabled = true;

    button.textContent =
        editingProductId
            ? "Saving..."
            : "Adding...";


    message.textContent = "";


    try {

        if (editingProductId) {

            await apiRequest(
                `/products/${editingProductId}`,
                {
                    method: "PUT",

                    body: JSON.stringify({
                        name: name,
                        price: price
                    })
                }
            );


            closeProductModal();

            await loadProducts();

            showProductMessage(
                "Product updated successfully."
            );


        } else {

            await apiRequest(
                "/products",
                {
                    method: "POST",

                    body: JSON.stringify({
                        product_id: productId,
                        name: name,
                        price: price
                    })
                }
            );


            closeProductModal();

            await loadProducts();

            showProductMessage(
                "Product added successfully."
            );

        }


    } catch (error) {

        message.textContent =
            error.message;

    } finally {

        button.disabled = false;

        button.textContent =
            editingProductId
                ? "Save changes"
                : "Add product";

    }

}


function openDeleteModal(productId) {

    deletingProductId =
        productId;


    document.getElementById(
        "deleteModal"
    ).classList.add("show");

}


function closeDeleteModal() {

    document.getElementById(
        "deleteModal"
    ).classList.remove("show");


    deletingProductId = null;

}


async function deleteProduct() {

    if (!deletingProductId) {
        return;
    }


    const button =
        document.getElementById(
            "confirmDelete"
        );


    button.disabled = true;

    button.textContent =
        "Deleting...";


    try {

        await apiRequest(
            `/products/${deletingProductId}`,
            {
                method: "DELETE"
            }
        );


        closeDeleteModal();

        await loadProducts();

        showProductMessage(
            "Product deleted successfully."
        );


    } catch (error) {

        closeDeleteModal();

        showProductMessage(
            error.message,
            true
        );

    } finally {

        button.disabled = false;

        button.textContent =
            "Delete product";

    }

}


function formatPrice(price) {

    const value =
        Number(price);


    if (!Number.isFinite(value)) {
        return "₹0";
    }


    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value);

}


function showProductMessage(
    text,
    error = false
) {

    const element =
        document.getElementById(
            "productMessage"
        );


    element.textContent =
        text;


    element.className =
        error
            ? "product-message error"
            : "product-message success";


    setTimeout(() => {

        element.textContent = "";

        element.className =
            "product-message";

    }, 3500);

}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "user"
    );

    window.location.href =
        "login.html";

}