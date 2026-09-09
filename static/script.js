document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    /* =========================================================
       COEURSTEAM — SCRIPT PRINCIPAL
       ========================================================= */

    const CART_KEY = "coeursteam_cart";

    let cart = [];

    /* =========================================================
       OUTILS
       ========================================================= */

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatPrice(value) {
        const number = Number(value) || 0;

        return number.toLocaleString("fr-FR", {
            style: "currency",
            currency: "EUR"
        });
    }

    function saveCart() {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
    }

    function loadCart() {
        try {
            const saved = localStorage.getItem(CART_KEY);

            if (!saved) {
                cart = [];
                return;
            }

            const parsed = JSON.parse(saved);

            if (Array.isArray(parsed)) {
                cart = parsed;
            } else {
                cart = [];
            }
        } catch (error) {
            console.error("Erreur lors du chargement du panier :", error);
            cart = [];
        }
    }

    /* =========================================================
       ELEMENTS DU PANIER
       ========================================================= */

    const cartItems = document.getElementById("cartItems");
    const cartTotal = document.getElementById("cartTotal");
    const cartCount = document.getElementById("cartCount");

    const cartOverlay = document.getElementById("cartOverlay");
    const cartDrawer = document.getElementById("cartDrawer");

    /* =========================================================
       RECUPERER UNE CARTE PRODUIT
       ========================================================= */

    function getProductCard(id) {
        const cards = document.querySelectorAll(".product-card");

        for (const card of cards) {
            if (String(card.dataset.productId) === String(id)) {
                return card;
            }
        }

        return null;
    }

    /* =========================================================
       AJOUTER AU PANIER
       ========================================================= */

    function addToCart(id) {
        const card = getProductCard(id);

        if (!card) {
            console.error("Produit introuvable :", id);
            return;
        }

        const nameElement = card.querySelector("h3");
        const priceElement = card.querySelector(".price strong");
        const imageElement = card.querySelector("img");

        const name = nameElement
            ? nameElement.textContent.trim()
            : "Produit";

        const priceText = priceElement
            ? priceElement.textContent.trim()
            : "0";

        const price = parseFloat(
            priceText
                .replace(/\s/g, "")
                .replace("€", "")
                .replace(",", ".")
        ) || 0;

        const image = imageElement
            ? imageElement.getAttribute("src")
            : "";

        const existingItem = cart.find(function (item) {
            return String(item.id) === String(id);
        });

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                id: String(id),
                name: name,
                price: price,
                image: image,
                quantity: 1
            });
        }

        saveCart();
        updateCart();
        openCart();

        showAddedFeedback(card);
    }

    /* =========================================================
       OUVRIR LE PANIER
       ========================================================= */

    function openCart() {
        if (!cartOverlay || !cartDrawer) {
            console.error("Éléments du panier introuvables.");
            return;
        }

        cartDrawer.classList.add("active");
        cartOverlay.classList.add("active");
        document.body.classList.add("cart-open");
    }

    /* =========================================================
       FERMER LE PANIER
       ========================================================= */

    function closeCart() {
        if (!cartOverlay || !cartDrawer) {
            return;
        }

        cartDrawer.classList.remove("active");
        cartOverlay.classList.remove("active");
        document.body.classList.remove("cart-open");
    }

    /* =========================================================
       TOGGLE PANIER
       IMPORTANT :
       window.toggleCart permet au onclick="toggleCart()"
       présent dans index.html de fonctionner.
       ========================================================= */

    window.toggleCart = function () {
        if (!cartOverlay || !cartDrawer) {
            console.error("Éléments du panier introuvables.");
            return;
        }

        const isOpen = cartDrawer.classList.contains("active");

        if (isOpen) {
            closeCart();
        } else {
            openCart();
        }
    };

    /* =========================================================
       FEEDBACK AJOUT PRODUIT
       ========================================================= */

    function showAddedFeedback(card) {
        const button = card.querySelector(".add-button");

        if (!button) {
            return;
        }

        const originalText = button.textContent;

        button.textContent = "AJOUTÉ ✓";
        button.classList.add("added");

        setTimeout(function () {
            button.textContent = originalText;
            button.classList.remove("added");
        }, 1200);
    }

    /* =========================================================
       SUPPRIMER DU PANIER
       ========================================================= */

    function removeFromCart(id) {
        cart = cart.filter(function (item) {
            return String(item.id) !== String(id);
        });

        saveCart();
        updateCart();
    }

    /* =========================================================
       MODIFIER QUANTITE
       ========================================================= */

    function changeQuantity(id, amount) {
        const item = cart.find(function (product) {
            return String(product.id) === String(id);
        });

        if (!item) {
            return;
        }

        item.quantity += amount;

        if (item.quantity <= 0) {
            removeFromCart(id);
            return;
        }

        saveCart();
        updateCart();
    }

    /* =========================================================
       METTRE A JOUR LE PANIER
       ========================================================= */

    function updateCart() {
        if (!cartItems) {
            return;
        }

        if (cart.length === 0) {
            cartItems.innerHTML = `
                <div class="empty-cart">
                    <span>♡</span>
                    <p>Votre panier est vide.</p>
                </div>
            `;

            if (cartTotal) {
                cartTotal.textContent = formatPrice(0);
            }

            if (cartCount) {
                cartCount.textContent = "0";
            }

            return;
        }

        let html = "";
        let total = 0;
        let count = 0;

        cart.forEach(function (item) {
            const price = Number(item.price) || 0;
            const quantity = Number(item.quantity) || 1;
            const totalItem = price * quantity;

            total += totalItem;
            count += quantity;

            html += `
                <div class="cart-item">

                    <div class="cart-item-image">
                        ${
                            item.image
                                ? `
                                    <img
                                        src="${escapeHtml(item.image)}"
                                        alt="${escapeHtml(item.name)}"
                                    >
                                  `
                                : ""
                        }
                    </div>

                    <div class="cart-item-info">

                        <strong>
                            ${escapeHtml(item.name)}
                        </strong>

                        <span>
                            ${formatPrice(price)}
                        </span>

                        <div class="cart-item-controls">

                            <button
                                type="button"
                                class="quantity-minus"
                                data-id="${escapeHtml(item.id)}"
                                aria-label="Diminuer la quantité"
                            >
                                −
                            </button>

                            <span>
                                ${quantity}
                            </span>

                            <button
                                type="button"
                                class="quantity-plus"
                                data-id="${escapeHtml(item.id)}"
                                aria-label="Augmenter la quantité"
                            >
                                +
                            </button>

                        </div>

                    </div>

                    <div class="cart-item-right">

                        <strong>
                            ${formatPrice(totalItem)}
                        </strong>

                        <button
                            type="button"
                            class="remove-cart-item"
                            data-id="${escapeHtml(item.id)}"
                            aria-label="Supprimer"
                        >
                            ×
                        </button>

                    </div>

                </div>
            `;
        });

        cartItems.innerHTML = html;

        if (cartTotal) {
            cartTotal.textContent = formatPrice(total);
        }

        if (cartCount) {
            cartCount.textContent = String(count);
        }
    }

    /* =========================================================
       OUVRIR LE PANIER
       ========================================================= */

    function openCart() {
        if (cartOverlay) {
            cartOverlay.classList.add("active");
        }

        if (cartDrawer) {
            cartDrawer.classList.add("active");
        }

        document.body.classList.add("cart-open");
    }

    /* =========================================================
       FERMER LE PANIER
       ========================================================= */

    function closeCart() {
        if (cartOverlay) {
            cartOverlay.classList.remove("active");
        }

        if (cartDrawer) {
            cartDrawer.classList.remove("active");
        }

        document.body.classList.remove("cart-open");
    }

    /* =========================================================
       EVENEMENTS PANIER
       ========================================================= */

    document.addEventListener("click", function (event) {

        const addButton = event.target.closest(".add-button");

        if (addButton) {
            const card = addButton.closest(".product-card");

            if (card) {
                const id = card.dataset.productId;

                if (id) {
                    addToCart(id);
                }
            }

            return;
        }

        const plusButton = event.target.closest(".quantity-plus");

        if (plusButton) {
            changeQuantity(plusButton.dataset.id, 1);
            return;
        }

        const minusButton = event.target.closest(".quantity-minus");

        if (minusButton) {
            changeQuantity(minusButton.dataset.id, -1);
            return;
        }

        const removeButton = event.target.closest(".remove-cart-item");

        if (removeButton) {
            removeFromCart(removeButton.dataset.id);
            return;
        }

        const cartToggle = event.target.closest("[data-cart-toggle]");

        if (cartToggle) {
            openCart();
            return;
        }

        const cartClose = event.target.closest("[data-cart-close]");

        if (cartClose) {
            closeCart();
            return;
        }

        if (event.target === cartOverlay) {
            closeCart();
        }
    });

    /* =========================================================
       CHECKOUT STRIPE
       ========================================================= */

       /* =========================================================
       PAIEMENT STRIPE
       ========================================================= */

    window.checkout = async function () {

        if (cart.length === 0) {
            alert("Votre panier est vide.");
            return;
        }

        const checkoutButton = document.querySelector(".checkout-button");

        if (checkoutButton) {
            checkoutButton.disabled = true;
            checkoutButton.innerHTML = "REDIRECTION... <span>→</span>";
        }

        try {

            const response = await fetch(
                "/create-checkout-session",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        items: cart.map(function (item) {
                            return {
                                id: item.id,
                                quantity: item.quantity
                            };
                        })
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error ||
                    "Erreur lors de la création du paiement."
                );
            }

            if (!data.url) {
                throw new Error(
                    "Stripe n'a pas retourné d'URL de paiement."
                );
            }

            window.location.href = data.url;

        } catch (error) {

            console.error("Erreur Stripe :", error);

            alert(
                error.message ||
                "Impossible de lancer le paiement."
            );

            if (checkoutButton) {
                checkoutButton.disabled = false;
                checkoutButton.innerHTML =
                    "CONTINUER VERS LE PAIEMENT <span>→</span>";
            }
        }
    };

    /* =========================================================
       CONDITIONS D'UTILISATION
       ========================================================= */

    const welcomeScreen = document.getElementById("welcomeScreen");
    const welcomeTerms = document.getElementById("welcomeTerms");
    const welcomeCheckbox = document.getElementById("welcomeCheckbox");
    const welcomeCheckboxLabel =
        document.getElementById("welcomeCheckboxLabel");
    const enterSiteButton =
        document.getElementById("enterSiteButton");
    const scrollMessage =
        document.querySelector(".welcome-scroll-message");

    if (
        welcomeScreen &&
        welcomeTerms &&
        welcomeCheckbox &&
        enterSiteButton
    ) {

        /* Au départ, impossible de cocher */
        welcomeCheckbox.checked = false;
        welcomeCheckbox.disabled = true;
        enterSiteButton.disabled = true;

        /* =====================================================
           VERIFIER SI L'UTILISATEUR EST ARRIVE EN BAS
           ===================================================== */

        function checkTermsScroll() {

            const scrollTop = welcomeTerms.scrollTop;
            const visibleHeight = welcomeTerms.clientHeight;
            const totalHeight = welcomeTerms.scrollHeight;

            const reachedBottom =
                scrollTop + visibleHeight >= totalHeight - 15;

            if (reachedBottom) {

                welcomeCheckbox.disabled = false;

                if (welcomeCheckboxLabel) {
                    welcomeCheckboxLabel.classList.add("enabled");
                }

                if (scrollMessage) {
                    scrollMessage.classList.add("hidden");
                }

            } else {

                welcomeCheckbox.disabled = true;
                welcomeCheckbox.checked = false;
                enterSiteButton.disabled = true;

                if (welcomeCheckboxLabel) {
                    welcomeCheckboxLabel.classList.remove("enabled");
                }

                if (scrollMessage) {
                    scrollMessage.classList.remove("hidden");
                }
            }
        }

        /* Vérification pendant le défilement */
        welcomeTerms.addEventListener(
            "scroll",
            checkTermsScroll
        );

        /* =====================================================
           CASE A COCHER
           ===================================================== */

        welcomeCheckbox.addEventListener(
            "change",
            function () {

                if (welcomeCheckbox.disabled) {
                    welcomeCheckbox.checked = false;
                    return;
                }

                enterSiteButton.disabled =
                    !welcomeCheckbox.checked;
            }
        );

        /* =====================================================
           ENTRER SUR LE SITE
           ===================================================== */

        enterSiteButton.addEventListener(
            "click",
            function () {

                if (
                    welcomeCheckbox.disabled ||
                    !welcomeCheckbox.checked
                ) {
                    return;
                }

                welcomeScreen.classList.add("hidden");

                document.body.classList.remove(
                    "welcome-open"
                );

                setTimeout(function () {
                    welcomeScreen.style.display = "none";
                }, 500);
            }
        );

        /* Vérification initiale */
        setTimeout(function () {
            checkTermsScroll();
        }, 100);
    }

    /* =========================================================
       NAVIGATION FLUIDE
       ========================================================= */

    document.querySelectorAll('a[href^="#"]').forEach(
        function (link) {

            link.addEventListener("click", function (event) {

                const targetId =
                    link.getAttribute("href");

                if (
                    !targetId ||
                    targetId === "#"
                ) {
                    return;
                }

                const target =
                    document.querySelector(targetId);

                if (!target) {
                    return;
                }

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            });
        }
    );

    /* =========================================================
       TOUCHE ECHAP
       ========================================================= */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {
                closeCart();
            }
        }
    );

    /* =========================================================
       INITIALISATION
       ========================================================= */

    loadCart();
    updateCart();

    /* Fonctions accessibles globalement si nécessaire */
    window.addToCart = addToCart;
    window.removeFromCart = removeFromCart;
    window.changeQuantity = changeQuantity;
    window.updateCart = updateCart;
    window.openCart = openCart;
    window.closeCart = closeCart;

    console.log(
        "CoeurSteam — script.js chargé correctement."
    );
});