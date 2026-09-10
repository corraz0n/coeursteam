import os
import sqlite3

from datetime import datetime

import stripe
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    session
)


# =========================================================
# CONFIGURATION
# =========================================================

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
        "image": "images/ark.jpg",
        "tag": "STEAM",
        "description": """
ARK: Survival Evolved est un jeu de survie et d'aventure en monde ouvert.

Échoué sur une île mystérieuse, vous devez apprendre à survivre dans un environnement rempli de dinosaures et de nombreuses créatures préhistoriques.

Commencez sans équipement, explorez votre environnement, chassez, récoltez des ressources, fabriquez des objets, construisez votre abri et développez progressivement vos technologies.

Vous pouvez également capturer, apprivoiser, élever et utiliser différentes créatures pour vous aider dans votre progression.

ARK peut être joué seul ou avec d'autres joueurs et propose un vaste système de construction, de fabrication, d'exploration et de progression.

Genre : Action, aventure, survie, RPG et multijoueur.
Développeur : Studio Wildcard et autres studios associés.
Date de sortie : 27 août 2017.

Produit numérique Steam.
"""
    },

    {
        "id": "crimson-desert",
        "name": "Crimson Desert",
        "price": 3.56,
        "image": "images/crimson.jpg",
        "tag": "STEAM",
        "description": """
Crimson Desert est un jeu d'action-aventure en monde ouvert développé par Pearl Abyss.

L'aventure se déroule sur le continent de Pywel, une vaste terre marquée par les conflits et les dangers.

Vous accompagnez Kliff et les Crinières Grises dans une aventure où l'exploration, les combats et la découverte de nouvelles régions occupent une place centrale.

Parcourez de vastes paysages, découvrez des ruines, affrontez différents ennemis et explorez les mystères liés à l'Abysse.

Le monde ouvert permet d'explorer de nombreuses régions et de découvrir progressivement l'histoire et les événements qui façonnent Pywel.

Genre : Action, aventure et monde ouvert.
Développeur : Pearl Abyss.
Date de sortie : 19 mars 2026.

Produit numérique Steam.
"""
    },

    {
        "id": "dayz",
        "name": "DayZ",
        "price": 13.99,
        "image": "images/dayz.jpg",
        "tag": "STEAM",
        "description": """
DayZ est un jeu de survie multijoueur en monde ouvert développé par Bohemia Interactive.

Vous évoluez dans un monde post-apocalyptique ravagé par une mystérieuse infection et devez trouver les ressources nécessaires pour rester en vie.

La nourriture, l'eau, les médicaments, les armes et les équipements sont limités. Vous devez donc explorer les bâtiments et les différentes zones afin de trouver ce dont vous avez besoin.

Les autres survivants peuvent devenir des alliés ou représenter une menace. Vous pouvez coopérer avec eux ou choisir de survivre seul.

Chaque partie peut prendre une direction différente en fonction de vos rencontres, de vos décisions et de votre manière de gérer les ressources.

Genre : Survie, monde ouvert, zombies, FPS et multijoueur.
Développeur : Bohemia Interactive.
Date de sortie : 13 décembre 2018.

Produit numérique Steam.
"""
    },

    {
        "id": "fc26",
        "name": "FC 26",
        "price": 5.99,
        "image": "images/fc26.jpg",
        "tag": "STEAM",
        "description": """
EA SPORTS FC 26 propose une expérience de football avec différents modes de jeu et de nombreuses possibilités pour construire et développer votre équipe.

Le jeu propose notamment un mode tournoi international réunissant 48 équipes ainsi que différentes nouveautés dans les modes Manager et Carrière Joueur.

Vous pouvez participer à différents défis, développer votre carrière et profiter de nombreuses expériences liées au football.

Le jeu propose également différentes possibilités de jeu en solo et en multijoueur, avec des modes compétitifs et coopératifs.

Les joueurs peuvent également retrouver différents contenus et événements thématiques au cours de leur progression.

Genre : Football, sport, simulation et multijoueur.
Développeurs : EA Canada et EA Romania.
Éditeur : Electronic Arts.
Date de sortie : 25 septembre 2025.

Produit numérique Steam.
"""
    },

    {
        "id": "resident-evil-requiem",
        "name": "Resident Evil Requiem",
        "price": 4.99,
        "image": "images/resident-evil-requiem.jpg",
        "tag": "STEAM",
        "description": """
Resident Evil Requiem est un jeu d'horreur et de survie développé par Capcom.

Le jeu plonge le joueur dans une aventure sombre et intense où la survie est au centre de l'expérience.

Explorez des environnements inquiétants, découvrez les événements qui se cachent derrière l'histoire et affrontez différentes menaces.

L'expérience mélange exploration, action, survie et narration avec une atmosphère particulièrement sombre.

Les ressources et l'équipement doivent être gérés avec attention tandis que vous progressez dans l'aventure.

Genre : Horreur et survie, action, FPS, tir à la troisième personne et aventure.
Développeur : CAPCOM Co., Ltd.
Date de sortie : 26 février 2026.

Produit numérique Steam.
"""
    },

    {
        "id": "rv-there-yet",
        "name": "RV There Yet?",
        "price": 5.99,
        "image": "images/rv-there-yet.jpg",
        "tag": "STEAM",
        "description": """
RV There Yet? est une aventure coopérative basée sur la conduite et la physique.

Vous devez conduire votre véhicule de loisirs afin de rentrer chez vous tout en traversant différents environnements et en affrontant de nombreux obstacles.

La coopération joue un rôle important : vous et vos coéquipiers devez travailler ensemble pour déplacer le véhicule, franchir les passages difficiles et continuer votre voyage.

Le jeu mélange conduite, exploration, humour et situations imprévisibles.

Les déplacements et les obstacles reposent notamment sur un système physique qui peut rendre chaque trajet différent.

Genre : Aventure, coopération, conduite et multijoueur.
Développeur : Nuggets Entertainment.
Date de sortie : 21 octobre 2025.

Produit numérique Steam.
"""
    },

    {
        "id": "baldurs-gate-3",
        "name": "Baldur's Gate 3",
        "price": 3.99,
        "image": "images/baldurs-gate-3.jpg",
        "tag": "STEAM",
        "description": """
Baldur's Gate 3 est un jeu de rôle développé par Larian Studios dans l'univers de Dungeons & Dragons.

Créez votre personnage, choisissez votre classe et constituez votre groupe avant de partir à l'aventure dans les Royaumes Oubliés.

Vos décisions peuvent modifier le déroulement de l'histoire et influencer vos relations avec les différents personnages rencontrés.

Le jeu propose des combats au tour par tour, une importante personnalisation des personnages, de nombreuses quêtes et un monde rempli de secrets à découvrir.

Vous pouvez également vivre l'aventure en coopération avec d'autres joueurs.

Genre : RPG, aventure et stratégie.
Développeur : Larian Studios.
Date de sortie : 3 août 2023.

Produit numérique Steam.
"""
    },

    {
        "id": "arc-raiders",
        "name": "ARC Raiders",
        "price": 7.99,
        "image": "images/arc-raiders.jpg",
        "tag": "STEAM",
        "description": """
ARC Raiders est une aventure d'extraction multijoueur développée par Embark Studios.

Le jeu se déroule dans un futur où la Terre est ravagée par une mystérieuse menace mécanisée appelée ARC.

Les joueurs doivent descendre à la surface afin de récupérer des ressources et des équipements tout en faisant face aux dangereuses machines qui contrôlent le monde extérieur.

Vous pouvez fabriquer, réparer et améliorer votre équipement avant de repartir en expédition.

La surface est également occupée par d'autres joueurs : il faut donc décider quand combattre, quand coopérer et quand éviter les affrontements afin de pouvoir revenir avec son butin.

Genre : Extraction shooter, PvP, PvE, survie, action et multijoueur.
Développeur : Embark Studios.
Date de sortie : 30 octobre 2025.

Produit numérique Steam.
"""
    }
]


EPIC_PRODUCTS = []


PLAYSTATION_PRODUCTS = [
    {
        "id": "dragon-ball-xenoverse",
        "name": "Dragon Ball Xenoverse",
        "price": 8.50,
        "image": "images/dragon-ball-xenoverse.jpg",
        "tag": "PLAYSTATION",
        "description": "Dragon Ball Xenoverse sur PlayStation."
    },

    {
        "id": "fc-26-ps4-ps5",
        "name": "FC 26 — PS4 / PS5",
        "price": 13.64,
        "image": "images/fc-26-ps4-ps5.jpg",
        "tag": "PLAYSTATION",
        "description": "FC 26 compatible PlayStation 4 et PlayStation 5."
    },

    {
        "id": "the-last-of-us-remastered-ps4",
        "name": "The Last of Us Remastered — PS4",
        "price": 8.65,
        "image": "images/the-last-of-us-remastered-ps4.jpg",
        "tag": "PLAYSTATION",
        "description": "Licence numérique de The Last of Us Remastered pour PlayStation 4."
    },

    {
        "id": "playstation_full_access",
        "name": "LICENCE PLAYSTATION — FULL ACCESS",
        "price": 46.00,
        "image": "images/playstation-full-access.jpg",
        "tag": "PLAYSTATION",
        "description": """
Produit numérique PlayStation.

Contenu inclus :

1. Grand Theft Auto Online — PlayStation 5
2. Call of Duty: Black Ops II
3. Subnautica
4. Firewatch
5. Goat Simulator 3
6. Goat Simulator
7. Plants vs. Zombies: La Bataille de Neighborville
8. The Exit 8
9. I Am Bread
10. Suicide Guy
"""
    }
]


# =========================================================
# TOUS LES PRODUITS
# =========================================================

ALL_PRODUCTS = (
    STEAM_PRODUCTS
    + EPIC_PRODUCTS
    + PLAYSTATION_PRODUCTS
)

PRODUCTS_BY_ID = {
    product["id"]: product
    for product in ALL_PRODUCTS
}


# =========================================================
# JEUX PLAYSTATION
# =========================================================

GAMES = {
    "gta-online": {
        "name": "Grand Theft Auto Online",
        "platform": "PlayStation 5",
        "description": "Explorez Los Santos, participez à des activités et construisez votre empire criminel dans GTA Online.",
        "image": "images/gta-online.jpg"
    },

    "black-ops-2": {
        "name": "Call of Duty: Black Ops II",
        "platform": "PlayStation",
        "description": "Un jeu de tir à la première personne mêlant campagne, multijoueur et mode Zombies.",
        "image": "images/black-ops-2.jpg"
    },

    "subnautica": {
        "name": "Subnautica",
        "platform": "PlayStation",
        "description": "Survivez et explorez un vaste monde sous-marin rempli de créatures, de ressources et de mystères.",
        "image": "images/subnautica.jpg"
    },

    "firewatch": {
        "name": "Firewatch",
        "platform": "PlayStation",
        "description": "Une aventure narrative à la première personne se déroulant dans les forêts du Wyoming.",
        "image": "images/firewatch.jpg"
    },

    "goat-simulator-3": {
        "name": "Goat Simulator 3",
        "platform": "PlayStation",
        "description": "Une aventure complètement déjantée où vous incarnez une chèvre dans un monde ouvert rempli de possibilités.",
        "image": "images/goat-simulator-3.jpg"
    },

    "goat-simulator": {
        "name": "Goat Simulator",
        "platform": "PlayStation",
        "description": "Incarnez une chèvre et semez le chaos dans un monde ouvert rempli de situations absurdes.",
        "image": "images/goat-simulator.jpg"
    },

    "plants-vs-zombies-neighborville": {
        "name": "Plants vs. Zombies: La Bataille de Neighborville",
        "platform": "PlayStation",
        "description": "Affrontez les zombies et les plantes dans des batailles délirantes à travers Neighborville.",
        "image": "images/plants-vs-zombies-neighborville.jpg"
    },

    "the-exit-8": {
        "name": "The Exit 8",
        "platform": "PlayStation",
        "description": "Repérez les anomalies et trouvez la sortie dans un mystérieux couloir qui semble se répéter sans fin.",
        "image": "images/the-exit-8.jpg"
    },

    "i-am-bread": {
        "name": "I Am Bread",
        "platform": "PlayStation",
        "description": "Devenez une tranche de pain et tentez de réaliser votre rêve ultime : devenir du pain grillé.",
        "image": "images/i-am-bread.jpg"
    },

    "suicide-guy": {
        "name": "Suicide Guy",
        "platform": "PlayStation",
        "description": "Résolvez des énigmes et traversez des mondes surréalistes dans cette aventure basée sur les rêves.",
        "image": "images/suicide-guy.jpg"
    }
}


# =========================================================
# PAGE D'UN JEU
# =========================================================

@app.route("/game/<game_id>")
def game_page(game_id):

    game = GAMES.get(game_id)

    if not game:
        return "Jeu introuvable", 404

    return render_template(
        "game.html",
        game=game
    )


@app.route("/comments", methods=["GET", "POST"])
def comments_page():

    connection = get_db()

    if request.method == "POST":

        comment = request.form.get("comment", "").strip()

        if comment:
            connection.execute(
                """
                INSERT INTO public_comments
                (product_id, order_id, comment, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "site",
                    0,
                    comment,
                    datetime.now().isoformat()
                )
            )

            connection.commit()

    comments = connection.execute(
        """
        SELECT comment, created_at
        FROM public_comments
        WHERE product_id = ?
        ORDER BY created_at DESC
        """,
        ("site",)
    ).fetchall()

    connection.close()

    return render_template(
        "comments.html",
        comments=comments
    )

# =========================================================
# PRODUITS TENDANCE
# =========================================================

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

    # -----------------------------------------------------
    # TABLE COMMANDES
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stripe_session_id TEXT UNIQUE NOT NULL,
            email TEXT,
            total REAL NOT NULL,
            comment TEXT,
            status TEXT NOT NULL DEFAULT 'paid',
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # AJOUT AUTOMATIQUE DE LA COLONNE COMMENT
    # POUR LES ANCIENNES BASES DE DONNÉES
    # -----------------------------------------------------

    try:

        connection.execute(
            "ALTER TABLE orders ADD COLUMN comment TEXT"
        )

    except sqlite3.OperationalError:

        pass

    # -----------------------------------------------------
    # TABLE PRODUITS COMMANDÉS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # TABLE MESSAGES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # TABLE COMMENTAIRES PUBLICS
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS public_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            order_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

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


@app.route("/product/<product_id>")
def product_page(product_id):

    product = PRODUCTS_BY_ID.get(product_id)

    if not product:
        return "Produit introuvable", 404

    connection = get_db()

    comments = connection.execute(
        """
        SELECT comment, created_at
        FROM public_comments
        WHERE product_id = ?
        ORDER BY created_at DESC
        """,
        (product_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "product.html",
        product=product,
        comments=comments
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
        trending_products=[],
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

        # -------------------------------------------------
        # COMMENTAIRE DE COMMANDE
        # -------------------------------------------------

        comment = str(
            data.get("comment", "")
        ).strip()

        if len(comment) > 1000:

            return jsonify({
                "error": "Le commentaire est trop long."
            }), 400

        # -------------------------------------------------
        # PRODUITS STRIPE
        # -------------------------------------------------

        line_items = []

        for item in items:

            product_id = str(
                item.get("id", "")
            )

            try:

                quantity = int(
                    item.get("quantity", 1)
                )

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
                        round(
                            product["price"] * 100
                        )
                    )
                },

                "quantity": quantity
            })

        # -------------------------------------------------
        # CRÉATION SESSION STRIPE
        # -------------------------------------------------

        checkout_session = stripe.checkout.Session.create(

            mode="payment",

            line_items=line_items,

            metadata={
                "order_comment": comment
            },

            success_url=(
                BASE_URL
                + "/success?session_id={CHECKOUT_SESSION_ID}"
            ),

            cancel_url=BASE_URL + "/"
        )

        print(
            "SESSION STRIPE CRÉÉE :",
            checkout_session.id
        )

        return jsonify({
            "url": checkout_session.url
        })

    except stripe.error.StripeError as error:

        print(
            "Erreur Stripe :",
            error
        )

        return jsonify({
            "error": str(error)
        }), 500

    except Exception as error:

        print(
            "Erreur serveur :",
            error
        )

        return jsonify({
            "error": "Erreur lors de la création du paiement."
        }), 500


# =========================================================
# PAGE APRÈS PAIEMENT
# =========================================================

@app.route("/success")
def success():

    session_id = request.args.get(
        "session_id"
    )

    print(
        "SESSION ID REÇU :",
        session_id
    )

    if not session_id:

        return "Session Stripe manquante", 400

    try:

        stripe_session = stripe.checkout.Session.retrieve(
            session_id
        )

        if stripe_session.payment_status != "paid":

            return "Paiement non confirmé", 400

        session_data = stripe_session.to_dict()

        connection = get_db()

        # -------------------------------------------------
        # VÉRIFIER SI LA COMMANDE EXISTE DÉJÀ
        # -------------------------------------------------

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

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        email = (
            session_data
            .get("customer_details", {})
            .get("email")
        )

        # -------------------------------------------------
        # COMMENTAIRE
        # -------------------------------------------------

        comment = (
            session_data
            .get("metadata", {})
            .get("order_comment", "")
        )

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        amount_total = session_data.get(
            "amount_total",
            0
        )

        total = amount_total / 100

        created_at = datetime.utcnow().isoformat()

        # -------------------------------------------------
        # CRÉER LA COMMANDE
        # -------------------------------------------------

        cursor = connection.execute(
            """
            INSERT INTO orders (
                stripe_session_id,
                email,
                total,
                comment,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                email,
                total,
                comment,
                "paid",
                created_at
            )
        )

        order_id = cursor.lastrowid

        print(
            "Commande créée depuis success :",
            order_id
        )

        # -------------------------------------------------
        # PRODUITS PAYÉS
        # -------------------------------------------------

        line_items = stripe.checkout.Session.list_line_items(
            session_id,
            limit=100
        )

        purchased_products = []

        for item in line_items.data:

            product_name = (
                item.description
                or "Produit"
            )

            quantity = (
                item.quantity
                or 1
            )

            unit_amount = 0

            if (
                item.price
                and item.price.unit_amount
            ):

                unit_amount = (
                    item.price.unit_amount
                    / 100
                )

            product_id = None

            for product in ALL_PRODUCTS:

                if (
                    product["name"].lower()
                    == product_name.lower()
                ):

                    product_id = product["id"]

                    break

            if not product_id:

                product_id = "unknown"

            # -------------------------------------------------
            # COMMENTAIRE PUBLIC
            # -------------------------------------------------

            if comment and product_id != "unknown":

                connection.execute(
                    """
                    INSERT INTO public_comments (
                        product_id,
                        order_id,
                        comment,
                        created_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        order_id,
                        comment,
                        created_at
                    )
                )

            # -------------------------------------------------
            # PRODUIT COMMANDÉ
            # -------------------------------------------------

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

            products_text = (
                "• Produit introuvable"
            )

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

        print(
            "ERREUR SUCCESS :",
            repr(error)
        )

        traceback.print_exc()

        return (
            f"Erreur serveur : {error}",
            500
        )


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():

    payload = request.data

    signature = request.headers.get(
        "Stripe-Signature"
    )

    if not STRIPE_WEBHOOK_SECRET:

        print(
            "STRIPE_WEBHOOK_SECRET non configuré."
        )

        return "Webhook non configuré", 500

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET
        )

    except ValueError:

        print(
            "Payload Stripe invalide."
        )

        return "Payload invalide", 400

    except stripe.error.SignatureVerificationError:

        print(
            "Signature Stripe invalide."
        )

        return "Signature invalide", 400

    event_type = event.get("type")

    print(
        "Webhook Stripe :",
        event_type
    )

    if event_type == "checkout.session.completed":

        stripe_session = (
            event["data"]["object"]
        )

        session_id = stripe_session.get(
            "id"
        )

        customer_details = (
            stripe_session.get(
                "customer_details"
            )
        )

        email = (
            customer_details.get("email")
            if customer_details
            else None
        )

        # -------------------------------------------------
        # COMMENTAIRE
        # -------------------------------------------------

        metadata = (
            stripe_session.get(
                "metadata"
            )
            or {}
        )

        comment = (
            metadata.get(
                "order_comment",
                ""
            )
            or ""
        )

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        amount_total = stripe_session.get(
            "amount_total",
            0
        )

        total = amount_total / 100

        created_at = datetime.utcnow().isoformat()

        connection = get_db()

        try:

            # -------------------------------------------------
            # VÉRIFIER SI LA COMMANDE EXISTE
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
                    comment,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    email,
                    total,
                    comment,
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
            # RÉCUPÉRER LES PRODUITS
            # -------------------------------------------------

            line_items = stripe.checkout.Session.list_line_items(
                session_id,
                limit=100
            )

            purchased_products = []

            for item in line_items.data:

                product_name = (
                    item.description
                    or "Produit"
                )

                quantity = (
                    item.quantity
                    or 1
                )

                unit_amount = 0

                if (
                    item.price
                    and item.price.unit_amount
                ):

                    unit_amount = (
                        item.price.unit_amount
                        / 100
                    )

                product_id = None

                for product in ALL_PRODUCTS:

                    if (
                        product["name"].lower()
                        == product_name.lower()
                    ):

                        product_id = product["id"]

                        break

                if not product_id:

                    product_id = "unknown"

                # -------------------------------------------------
                # COMMENTAIRE PUBLIC
                # -------------------------------------------------

                if comment and product_id != "unknown":

                    connection.execute(
                        """
                        INSERT INTO public_comments (
                            product_id,
                            order_id,
                            comment,
                            created_at
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            product_id,
                            order_id,
                            comment,
                            created_at
                        )
                    )

                # -------------------------------------------------
                # PRODUIT COMMANDÉ
                # -------------------------------------------------

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

                products_text = (
                    "• Produit introuvable"
                )

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
# PAGE DE DISCUSSION / COMMANDE
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


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        if password == os.getenv(
            "ADMIN_PASSWORD"
        ):

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                url_for("admin_orders")
            )

        return (
            "Mot de passe incorrect",
            401
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN COMMANDES
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("admin_login")
        )

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
# ENVOYER UN MESSAGE CLIENT
# =========================================================

@app.route(
    "/order/<int:order_id>/message",
    methods=["POST"]
)
def send_order_message(order_id):

    message = request.form.get(
        "message",
        ""
    ).strip()

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
        url_for(
            "order_page",
            order_id=order_id
        )
    )


# =========================================================
# INITIALISATION
# =========================================================

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