import os
import sqlite3
from datetime import datetime

import stripe
from dotenv import load_dotenv

from flask import Flask, render_template, jsonify, request, redirect, url_for



load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key-in-production"
)

BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:5000"
)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

stripe.api_key = STRIPE_SECRET_KEY

if not stripe.api_key:
    raise RuntimeError(
        "STRIPE_SECRET_KEY est introuvable dans le fichier .env"
    )

print(
    "MODE STRIPE :",
    "TEST" if stripe.api_key.startswith("sk_test_") else "LIVE"
)


# =========================================================
# PRODUITS
# =========================================================

STEAM_PRODUCTS = [
    {
        "id": "ark",
        "name": "ARK: Survival Evolved",
        "price": 2.99,
        "image": "images/ark.jpg"
    },
    {
        "id": "crimson-desert",
        "name": "Crimson Desert",
        "price": 3.56,
        "image": "images/crimson.jpg"
    },
    {
        "id": "dayz",
        "name": "DayZ",
        "price": 13.99,
        "image": "images/dayz.jpg"
    },
    {
        "id": "fc26",
        "name": "FC 26",
        "price": 5.99,
        "image": "images/fc26.jpg"
    },
    {
        "id": "resident-evil-requiem",
        "name": "Resident Evil Requiem",
        "price": 4.99,
        "image": "images/resident-evil-requiem.jpg"
    },
    {
        "id": "rv-there-yet",
        "name": "RV There Yet?",
        "price": 5.99,
        "image": "images/rv-there-yet.jpg"
    },
    {
        "id": "baldurs-gate-3",
        "name": "Baldur's Gate 3",
        "price": 3.99,
        "image": "images/baldurs-gate-3.jpg"
    },
    {
        "id": "arc-raiders",
        "name": "ARC Raiders",
        "price": 7.99,
        "image": "images/arc-raiders.jpg"
    },
    {
        "id": "cod-black-ops-7",
        "name": "Call of Duty: Black Ops 7",
        "price": 17.86,
        "image": "images/cod-black-ops-7.jpg"
    },
    {
        "id": "battlefield-6",
        "name": "Battlefield 6",
        "price": 18.65,
        "image": "images/battlefield-6.jpg"
    },
    {
        "id": "cyberpunk-2077",
        "name": "Cyberpunk 2077",
        "price": 7.99,
        "image": "images/cyberpunk-2077.jpg"
    },
    {
        "id": "euro-truck-simulator-2",
        "name": "Euro Truck Simulator 2",
        "price": 3.99,
        "image": "images/euro-truck-simulator-2.jpg"
    },
    {
        "id": "diablo-xv",
        "name": "Diablo XV",
        "price": 14.99,
        "image": "images/diablo-xv.jpg"
    },
    {
        "id": "nioh-3",
        "name": "Nioh 3",
        "price": 2.99,
        "image": "images/nioh-3.jpg"
    },
    {
        "id": "escape-from-tarkov",
        "name": "Escape from Tarkov",
        "price": 12.37,
        "image": "images/escape-from-tarkov.jpg"
    },
    {
        "id": "constantce",
        "name": "Constantce",
        "price": 8.25,
        "image": "images/constantce.jpg"
    },
    {
        "id": "dont-starve-together",
        "name": "Don't Starve Together",
        "price": 2.99,
        "image": "images/dont-starve-together.jpg"
    },
    {
        "id": "of-ash-and-steel",
        "name": "Of Ash and Steel",
        "price": 14.99,
        "image": "images/of-ash-and-steel.jpg"
    },
    {
        "id": "sea-of-thieves",
        "name": "Sea of Thieves",
        "price": 6.99,
        "image": "images/sea-of-thieves.jpg"
    },
    {
        "id": "dead-by-daylight",
        "name": "Dead by Daylight",
        "price": 7.86,
        "image": "images/dead-by-daylight.jpg"
    },
    {
        "id": "ready-or-not",
        "name": "Ready or Not",
        "price": 7.42,
        "image": "images/ready-or-not.jpg"
    },
    {
        "id": "rust",
        "name": "Rust",
        "price": 7.86,
        "image": "images/rust.jpg"
    },
    {
        "id": "dispatch",
        "name": "Dispatch",
        "price": 3.99,
        "image": "images/dispatch.jpg"
    },
    {
        "id": "gtfo",
        "name": "GTFO",
        "price": 8.44,
        "image": "images/gtfo.jpg"
    },
    {
        "id": "raft",
        "name": "Raft",
        "price": 6.52,
        "image": "images/raft.jpg"
    }
]

EPIC_PRODUCTS = []

PLAYSTATION_PRODUCTS = []

ALL_PRODUCTS = (
    STEAM_PRODUCTS
    + EPIC_PRODUCTS
    + PLAYSTATION_PRODUCTS
)

PRODUCTS_BY_ID = {
    product["id"]: product
    for product in ALL_PRODUCTS
}


TRENDING_IDS = [
    "ark",
    "crimson-desert",
    "dayz",
    "fc26",
    "resident-evil-requiem",
    "rv-there-yet",
    "baldurs-gate-3",
    "arc-raiders"
]


def get_trending_products():
    products = []

    for product_id in TRENDING_IDS:
        product = PRODUCTS_BY_ID.get(product_id)

        if product:
            products.append(product)

    return products


# =========================================================
# BASE DE DONNÉES
# =========================================================

DATABASE = "coeursteam.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stripe_session_id TEXT UNIQUE NOT NULL,
            email TEXT,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'paid',
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# PAGES
# =========================================================

@app.route("/")
def home():
    return render_template(
        "index.html",
        products=STEAM_PRODUCTS,
        trending_products=get_trending_products(),
        platform="home"
    )


@app.route("/steam")
def steam():
    return render_template(
        "index.html",
        products=STEAM_PRODUCTS,
        trending_products=get_trending_products(),
        platform="steam"
    )


@app.route("/epic")
def epic():
    return render_template(
        "index.html",
        products=EPIC_PRODUCTS,
        trending_products=get_trending_products(),
        platform="epic"
    )


@app.route("/playstation")
def playstation():
    return render_template(
        "index.html",
        products=PLAYSTATION_PRODUCTS,
        trending_products=get_trending_products(),
        platform="playstation"
    )


# =========================================================
# STRIPE CHECKOUT
# =========================================================

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "Données du panier manquantes."
            }), 400

        items = data.get("items", [])

        if not isinstance(items, list) or not items:
            return jsonify({
                "error": "Le panier est vide."
            }), 400

        line_items = []

        for item in items:
            product_id = str(item.get("id", ""))

            try:
                quantity = int(item.get("quantity", 1))
            except (TypeError, ValueError):
                return jsonify({
                    "error": "Quantité invalide."
                }), 400

            if quantity < 1 or quantity > 99:
                return jsonify({
                    "error": "Quantité invalide."
                }), 400

            product = PRODUCTS_BY_ID.get(product_id)

            if not product:
                return jsonify({
                    "error": "Produit introuvable."
                }), 400

            line_items.append({
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": product["name"]
                    },
                    "unit_amount": int(
                        round(product["price"] * 100)
                    )
                },
                "quantity": quantity
            })

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=(
                BASE_URL
                + "/success?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=BASE_URL + "/"
        )

        print("SESSION STRIPE CRÉÉE :", checkout_session.id)

        return jsonify({
            "url": checkout_session.url
        })

    except stripe.error.StripeError as error:
        print("Erreur Stripe :", error)

        return jsonify({
            "error": str(error)
        }), 500

    except Exception as error:
        print("Erreur serveur :", error)

        return jsonify({
            "error": "Erreur lors de la création du paiement."
        }), 500


# =========================================================
# PAGE APRÈS PAIEMENT
# =========================================================


@app.route("/success")
def success():

    session_id = request.args.get("session_id")

    print("SESSION ID REÇU :", session_id)

    if not session_id:
        return "Session Stripe manquante", 400

  


    try:

        session = stripe.checkout.Session.retrieve(
            session_id
        )

        if session.payment_status != "paid":
            return "Paiement non confirmé", 400

        session_data = session.to_dict()

        connection = get_db()

        order = connection.execute(
            """
            SELECT id
            FROM orders
            WHERE stripe_session_id = ?
            """,
            (session_id,)
        ).fetchone()

        if order:

            order_id = order["id"]

            connection.close()

            return render_template(
                "success.html",
                session=session_data,
                session_id=session_id,
                order_id=order_id
            )

        email = (
            session_data.get("customer_details", {})
            .get("email")
        )

        amount_total = session_data.get(
            "amount_total",
            0
        )

        total = amount_total / 100

        created_at = datetime.utcnow().isoformat()

        cursor = connection.execute(
            """
            INSERT INTO orders (
                stripe_session_id,
                email,
                total,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                email,
                total,
                "paid",
                created_at
            )
        )

        order_id = cursor.lastrowid

        print(
            "Commande créée depuis success :",
            order_id
        )

        line_items = stripe.checkout.Session.list_line_items(
            session_id,
            limit=100
        )

        purchased_products = []

        for item in line_items.data:

            product_name = item.description or "Produit"

            quantity = item.quantity or 1

            unit_amount = 0

            if item.price and item.price.unit_amount:
                unit_amount = item.price.unit_amount / 100

            product_id = None

            for product in ALL_PRODUCTS:

                if product["name"].lower() == product_name.lower():
                    product_id = product["id"]
                    break

            if not product_id:
                product_id = "unknown"

            connection.execute(
                """
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    product_name,
                    quantity,
                    price
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    product_id,
                    product_name,
                    quantity,
                    unit_amount
                )
            )

            purchased_products.append(
                f"{product_name} x{quantity}"
            )

        if purchased_products:

            products_text = "\n".join(
                f"• {product}"
                for product in purchased_products
            )

        else:

            products_text = "• Produit introuvable"

        automatic_message = (
            "Bonjour et merci pour votre commande !\n\n"
            f"Commande #{order_id}\n\n"
            "Produit(s) commandé(s) :\n"
            f"{products_text}\n\n"
            f"Montant payé : {total:.2f} €\n"
            "Paiement confirmé par Stripe.\n\n"
            "Votre commande est maintenant prise en charge. "
            "Vous pouvez utiliser cet espace pour communiquer "
            "avec le vendeur concernant votre commande."
        )

        connection.execute(
            """
            INSERT INTO messages (
                order_id,
                sender,
                message,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                order_id,
                "system",
                automatic_message,
                created_at
            )
        )

        connection.commit()

        connection.close()

        print(
            "Discussion créée depuis success :",
            order_id
        )

        return render_template(
            "success.html",
            session=session_data,
            session_id=session_id,
            order_id=order_id
        )

    except Exception as error:

        import traceback

        print("ERREUR SUCCESS :", repr(error))
        traceback.print_exc()

        return f"Erreur serveur : {error}", 500



@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():

    payload = request.data
    signature = request.headers.get("Stripe-Signature")

    if not STRIPE_WEBHOOK_SECRET:
        print("STRIPE_WEBHOOK_SECRET non configuré.")
        return "Webhook non configuré", 500

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:

        print("Payload Stripe invalide.")
        return "Payload invalide", 400

    except stripe.error.SignatureVerificationError:

        print("Signature Stripe invalide.")
        return "Signature invalide", 400

    event_type = event.get("type")

    print("Webhook Stripe :", event_type)


    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        session_id = session.get("id")

        customer_details = session.get("customer_details")

        email = (
            customer_details.get("email")
            if customer_details
            else None
        )

        amount_total = session.get(
            "amount_total",
            0
        )

        total = amount_total / 100

        created_at = datetime.utcnow().isoformat()


        total = amount_total / 100

        created_at = datetime.utcnow().isoformat()

        connection = get_db()

        try:

            # -------------------------------------------------
            # VÉRIFIER SI LA COMMANDE EXISTE DÉJÀ
            # -------------------------------------------------

            existing_order = connection.execute(
                """
                SELECT id
                FROM orders
                WHERE stripe_session_id = ?
                """,
                (session_id,)
            ).fetchone()

            if existing_order:

                print(
                    "Commande déjà enregistrée :",
                    session_id
                )

                connection.close()

                return "OK", 200

            # -------------------------------------------------
            # CRÉATION DE LA COMMANDE
            # -------------------------------------------------

            cursor = connection.execute(
                """
                INSERT INTO orders (
                    stripe_session_id,
                    email,
                    total,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    email,
                    total,
                    "paid",
                    created_at
                )
            )

            order_id = cursor.lastrowid

            print(
                "Commande créée :",
                order_id
            )

            # -------------------------------------------------
            # RÉCUPÉRER LES PRODUITS PAYÉS SUR STRIPE
            # -------------------------------------------------

            line_items = stripe.checkout.Session.list_line_items(
                session_id,
                limit=100
            )

            purchased_products = []

            for item in line_items.data:

                product_name = item.description or "Produit"

                quantity = item.quantity or 1

                unit_amount = 0

                if item.price and item.price.unit_amount:
                    unit_amount = item.price.unit_amount / 100

                product_id = None

                for product in ALL_PRODUCTS:

                    if product["name"].lower() == product_name.lower():

                        product_id = product["id"]

                        break

                if not product_id:
                    product_id = "unknown"

                connection.execute(
                    """
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        product_name,
                        quantity,
                        price
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        product_id,
                        product_name,
                        quantity,
                        unit_amount
                    )
                )

                purchased_products.append(
                    f"{product_name} x{quantity}"
                )

            # -------------------------------------------------
            # MESSAGE AUTOMATIQUE
            # -------------------------------------------------

            if purchased_products:

                products_text = "\n".join(
                    f"• {product}"
                    for product in purchased_products
                )

            else:

                products_text = "• Produit introuvable"

            automatic_message = (
                "Bonjour et merci pour votre commande !\n\n"
                f"Commande #{order_id}\n\n"
                "Produit(s) commandé(s) :\n"
                f"{products_text}\n\n"
                f"Montant payé : {total:.2f} €\n"
                "Paiement confirmé par Stripe.\n\n"
                "Votre commande est maintenant prise en charge. "
                "Vous pouvez utiliser cet espace pour communiquer "
                "avec le vendeur concernant votre commande."
            )

            connection.execute(
                """
                INSERT INTO messages (
                    order_id,
                    sender,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    "system",
                    automatic_message,
                    created_at
                )
            )

            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            connection.commit()

            print(
                "Discussion créée automatiquement pour la commande :",
                order_id
            )

        except Exception as error:

            connection.rollback()

            print(
                "Erreur création commande :",
                error
            )

            connection.close()

            return "Erreur serveur", 500

        connection.close()

    return "OK", 200



    





# =========================================================
# PAGE DE DISCUSSION
# =========================================================

@app.route("/order/<int:order_id>")
def order_page(order_id):

    connection = get_db()

    order = connection.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if not order:

        connection.close()

        return "Commande introuvable", 404

    items = connection.execute(
        """
        SELECT *
        FROM order_items
        WHERE order_id = ?
        """,
        (order_id,)
    ).fetchall()

    messages = connection.execute(
        """
        SELECT *
        FROM messages
        WHERE order_id = ?
        ORDER BY created_at ASC
        """,
        (order_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "order.html",
        order=order,
        items=items,
        messages=messages
    )
             

@app.route("/admin/orders")
def admin_orders():

    connection = get_db()

    orders = connection.execute(
        """
        SELECT *
        FROM orders
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


# =========================================================
# INITIALISATION
# =========================================================


@app.route("/order/<int:order_id>/message", methods=["POST"])
def send_order_message(order_id):

    message = request.form.get("message", "").strip()

    if not message:
        return "Message vide", 400

    connection = get_db()

    order = connection.execute(
        """
        SELECT id
        FROM orders
        WHERE id = ?
        """,
        (order_id,)
    ).fetchone()

    if not order:
        connection.close()
        return "Commande introuvable", 404

    connection.execute(
        """
        INSERT INTO messages (
            order_id,
            sender,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            order_id,
            "customer",
            message,
            datetime.utcnow().isoformat()
        )
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("order_page", order_id=order_id)
    )



init_database()


# =========================================================
# LANCEMENT
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )