from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from pathlib import Path
import json


# ============================================================
# CONFIGURATION
# ============================================================

from config import (
    SECRET_KEY,
    DEFAULT_LANGUAGE,
    LANGUAGES,
    RTL_LANGUAGES,
    UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH
)


# ============================================================
# DATABASE
# ============================================================

from database.db import (
    get_db,
    close_db,
    init_db
)


# ============================================================
# MATCHING
# ============================================================

from services.matching import find_all_matches


# ============================================================
# ROUTES
# ============================================================

from routes import auth
from routes import lost
from routes import found
from routes import match


# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = SECRET_KEY

app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

app.config["UPLOAD_FOLDER"] = str(
    UPLOAD_FOLDER
)


# ============================================================
# CREATE UPLOAD FOLDER
# ============================================================

Path(
    UPLOAD_FOLDER
).mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATABASE CLOSE
# ============================================================

app.teardown_appcontext(
    close_db
)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

with app.app_context():

    try:

        init_db()

        print(
            "MySQL database initialized successfully."
        )

    except Exception as error:

        print(
            "Database initialization error:",
            error
        )


# ============================================================
# TRANSLATION FUNCTION
# ============================================================

def load_translation(language):

    translation_folder = (
        Path(__file__).resolve().parent
        / "translations"
    )

    translation_file = (
        translation_folder
        / f"{language}.json"
    )

    # --------------------------------------------------------
    # If requested language does not exist
    # --------------------------------------------------------

    if not translation_file.exists():

        translation_file = (
            translation_folder
            / f"{DEFAULT_LANGUAGE}.json"
        )

    try:

        with open(
            translation_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            "Translation loading error:",
            error
        )

        return {}


# ============================================================
# TRANSLATION CONTEXT
# ============================================================

@app.context_processor
def inject_translations():

    current_language = session.get(
        "language",
        DEFAULT_LANGUAGE
    )

    # --------------------------------------------------------
    # Validate language
    # --------------------------------------------------------

    if current_language not in LANGUAGES:

        current_language = DEFAULT_LANGUAGE

    translations = load_translation(
        current_language
    )

    # --------------------------------------------------------
    # Translation helper
    # --------------------------------------------------------

    def translate(key):

        return translations.get(
            key,
            key
        )

    # --------------------------------------------------------
    # RTL / LTR
    # --------------------------------------------------------

    page_direction = (
        "rtl"
        if current_language in RTL_LANGUAGES
        else "ltr"
    )

    return {
        "t": translate,
        "languages": LANGUAGES,
        "current_language": current_language,
        "page_direction": page_direction
    }


# ============================================================
# LANGUAGE SWITCH
# ============================================================

@app.route(
    "/set-language",
    methods=["POST"]
)
def set_language():

    language = request.form.get(
        "language",
        DEFAULT_LANGUAGE
    )

    if language not in LANGUAGES:

        language = DEFAULT_LANGUAGE

    session["language"] = language

    return redirect(
        request.referrer
        or url_for("home")
    )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    db = get_db()

    # --------------------------------------------------------
    # Latest LOST items
    # --------------------------------------------------------

    lost_cursor = db.execute(
        """
        SELECT
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        LEFT JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.status = 'lost'
        ORDER BY lost_items.created_at DESC
        LIMIT 6
        """
    )

    lost_items = lost_cursor.fetchall()

    lost_cursor.close()

    # --------------------------------------------------------
    # Latest FOUND items
    # --------------------------------------------------------

    found_cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        LEFT JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.status = 'found'
        ORDER BY found_items.created_at DESC
        LIMIT 6
        """
    )

    found_items = found_cursor.fetchall()

    found_cursor.close()

    # --------------------------------------------------------
    # SMART MATCHING
    # --------------------------------------------------------

    smart_matches = []

    try:

        if lost_items and found_items:

            smart_matches = find_all_matches(
                lost_items,
                found_items
            )

            smart_matches = smart_matches[:6]

            # ------------------------------------------------
            # Add reporter names again if matching service
            # returned incomplete item dictionaries.
            # ------------------------------------------------

            for smart_match in smart_matches:

                lost_item = smart_match.get(
                    "lost_item",
                    {}
                )

                found_item = smart_match.get(
                    "found_item",
                    {}
                )

                # --------------------------------------------
                # Lost reporter
                # --------------------------------------------

                if (
                    isinstance(lost_item, dict)
                    and not lost_item.get("reporter_name")
                    and lost_item.get("id")
                ):

                    cursor = db.execute(
                        """
                        SELECT
                            lost_items.*,
                            users.name AS reporter_name
                        FROM lost_items
                        LEFT JOIN users
                            ON lost_items.user_id = users.id
                        WHERE lost_items.id = ?
                        LIMIT 1
                        """,
                        (
                            lost_item.get("id"),
                        )
                    )

                    complete_lost = cursor.fetchone()

                    cursor.close()

                    if complete_lost:

                        smart_match[
                            "lost_item"
                        ] = complete_lost

                # --------------------------------------------
                # Found reporter
                # --------------------------------------------

                if (
                    isinstance(found_item, dict)
                    and not found_item.get("reporter_name")
                    and found_item.get("id")
                ):

                    cursor = db.execute(
                        """
                        SELECT
                            found_items.*,
                            users.name AS reporter_name
                        FROM found_items
                        LEFT JOIN users
                            ON found_items.user_id = users.id
                        WHERE found_items.id = ?
                        LIMIT 1
                        """,
                        (
                            found_item.get("id"),
                        )
                    )

                    complete_found = cursor.fetchone()

                    cursor.close()

                    if complete_found:

                        smart_match[
                            "found_item"
                        ] = complete_found

    except Exception as error:

        print(
            "Home smart matching error:",
            error
        )

        smart_matches = []

    # --------------------------------------------------------
    # HOME TEMPLATE
    # --------------------------------------------------------

    return render_template(
        "index.html",
        lost_items=lost_items,
        found_items=found_items,
        smart_matches=smart_matches
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    # --------------------------------------------------------
    # Login check
    # --------------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please login to view your dashboard.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    user_id = session["user_id"]

    db = get_db()

    # --------------------------------------------------------
    # User information
    # --------------------------------------------------------

    user_cursor = db.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        LIMIT 1
        """,
        (
            user_id,
        )
    )

    user = user_cursor.fetchone()

    user_cursor.close()

    # --------------------------------------------------------
    # User's LOST items
    # --------------------------------------------------------

    lost_cursor = db.execute(
        """
        SELECT
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        LEFT JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.user_id = ?
        ORDER BY lost_items.created_at DESC
        """,
        (
            user_id,
        )
    )

    user_lost_items = lost_cursor.fetchall()

    lost_cursor.close()

    # --------------------------------------------------------
    # User's FOUND items
    # --------------------------------------------------------

    found_cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        LEFT JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.user_id = ?
        ORDER BY found_items.created_at DESC
        """,
        (
            user_id,
        )
    )

    user_found_items = found_cursor.fetchall()

    found_cursor.close()

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    return render_template(
        "dashboard.html",
        user=user,
        lost_items=user_lost_items,
        found_items=user_found_items
    )


# ============================================================
# BLUEPRINT HELPER
# ============================================================

def get_blueprint(
    module,
    possible_names
):
    """
    Find a blueprint inside a route module.

    This makes the application compatible with:
        lost_bp
        found_bp
        match_bp
        auth
        auth_bp
        bp
    """

    for name in possible_names:

        blueprint = getattr(
            module,
            name,
            None
        )

        if blueprint is not None:

            return blueprint

    raise AttributeError(
        f"{module.__name__} must contain one of: "
        + ", ".join(possible_names)
    )


# ============================================================
# REGISTER AUTH BLUEPRINT
# ============================================================

auth_blueprint = get_blueprint(
    auth,
    [
        "auth",
        "auth_bp",
        "bp"
    ]
)

app.register_blueprint(
    auth_blueprint
)


# ============================================================
# REGISTER LOST BLUEPRINT
# ============================================================

lost_blueprint = get_blueprint(
    lost,
    [
        "lost_bp",
        "lost",
        "bp"
    ]
)

app.register_blueprint(
    lost_blueprint
)


# ============================================================
# REGISTER FOUND BLUEPRINT
# ============================================================

found_blueprint = get_blueprint(
    found,
    [
        "found_bp",
        "found",
        "bp"
    ]
)

app.register_blueprint(
    found_blueprint
)


# ============================================================
# REGISTER MATCH BLUEPRINT
# ============================================================

match_blueprint = get_blueprint(
    match,
    [
        "match_bp",
        "match",
        "bp"
    ]
)

app.register_blueprint(
    match_blueprint
)


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "base.html"
    ), 404


# ============================================================
# 413 ERROR - FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded file is too large. Maximum size is 5 MB.",
        "error"
    )

    return redirect(
        request.referrer
        or url_for("home")
    )


# ============================================================
# 500 ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print(
        "Internal server error:",
        error
    )

    return render_template(
        "base.html"
    ), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )