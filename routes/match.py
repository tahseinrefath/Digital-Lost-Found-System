from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    flash
)

from database.db import get_db
from services.matching import find_all_matches


# ============================================================
# MATCH BLUEPRINT
# ============================================================

match_bp = Blueprint(
    "match",
    __name__
)


# ============================================================
# LOGIN CHECK
# ============================================================

def login_required():
    return "user_id" in session


# ============================================================
# GET COMPLETE LOST ITEM
# ============================================================

def get_lost_item(db, item_id):

    if not item_id:
        return {}

    cursor = db.execute(
        """
        SELECT
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        INNER JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.id = ?
        LIMIT 1
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    cursor.close()

    return item if item else {}


# ============================================================
# GET COMPLETE FOUND ITEM
# ============================================================

def get_found_item(db, item_id):

    if not item_id:
        return {}

    cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        INNER JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.id = ?
        LIMIT 1
        """,
        (item_id,)
    )

    item = cursor.fetchone()

    cursor.close()

    return item if item else {}


# ============================================================
# MATCHES PAGE
# ============================================================

@match_bp.route("/matches")
def matches():

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    if not login_required():

        flash(
            "Please login to view matches.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    db = get_db()

    # --------------------------------------------------------
    # Get LOST items
    # --------------------------------------------------------

    lost_cursor = db.execute(
        """
        SELECT
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        INNER JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.status = 'lost'
        ORDER BY lost_items.created_at DESC
        """
    )

    lost_items = lost_cursor.fetchall()

    lost_cursor.close()

    # --------------------------------------------------------
    # Get FOUND items
    # --------------------------------------------------------

    found_cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        INNER JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.status = 'found'
        ORDER BY found_items.created_at DESC
        """
    )

    found_items = found_cursor.fetchall()

    found_cursor.close()

    # --------------------------------------------------------
    # Find matches
    # --------------------------------------------------------

    raw_matches = []

    try:

        if lost_items and found_items:

            raw_matches = find_all_matches(
                lost_items,
                found_items
            )

    except Exception as error:

        print(
            "Matching error:",
            error
        )

        raw_matches = []

    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    try:

        raw_matches.sort(
            key=lambda item: float(
                item.get(
                    "similarity",
                    item.get(
                        "score",
                        item.get(
                            "match_score",
                            0
                        )
                    )
                )
            ),
            reverse=True
        )

    except Exception as error:

        print(
            "Match sorting error:",
            error
        )

    # --------------------------------------------------------
    # Maximum 10
    # --------------------------------------------------------

    raw_matches = raw_matches[:10]

    # --------------------------------------------------------
    # Prepare final matches
    # --------------------------------------------------------

    prepared_matches = []

    for raw_match in raw_matches:

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        similarity = raw_match.get(
            "similarity",
            raw_match.get(
                "score",
                raw_match.get(
                    "match_score",
                    0
                )
            )
        )

        try:

            similarity = float(
                similarity
            )

        except (TypeError, ValueError):

            similarity = 0

        similarity = max(
            0,
            min(
                similarity,
                100
            )
        )

        # ----------------------------------------------------
        # Lost item
        # ----------------------------------------------------

        lost_item = raw_match.get(
            "lost_item",
            {}
        )

        # ----------------------------------------------------
        # Found item
        # ----------------------------------------------------

        found_item = raw_match.get(
            "found_item",
            {}
        )

        # ----------------------------------------------------
        # Lost ID
        # ----------------------------------------------------

        lost_id = None

        if isinstance(
            lost_item,
            dict
        ):

            lost_id = (
                lost_item.get("id")
                or lost_item.get("lost_id")
                or lost_item.get("item_id")
            )

        if not lost_id:

            lost_id = raw_match.get(
                "lost_id"
            )

        # ----------------------------------------------------
        # Found ID
        # ----------------------------------------------------

        found_id = None

        if isinstance(
            found_item,
            dict
        ):

            found_id = (
                found_item.get("id")
                or found_item.get("found_id")
                or found_item.get("item_id")
            )

        if not found_id:

            found_id = raw_match.get(
                "found_id"
            )

        # ----------------------------------------------------
        # Get complete LOST item
        # ----------------------------------------------------

        if lost_id:

            database_lost_item = get_lost_item(
                db,
                lost_id
            )

            if database_lost_item:

                lost_item = database_lost_item

        # ----------------------------------------------------
        # Get complete FOUND item
        # ----------------------------------------------------

        if found_id:

            database_found_item = get_found_item(
                db,
                found_id
            )

            if database_found_item:

                found_item = database_found_item

        # ----------------------------------------------------
        # Match level
        # ----------------------------------------------------

        if similarity >= 75:

            match_level = "high"
            match_label = "High Match"

        elif similarity >= 50:

            match_level = "medium"
            match_label = "Medium Match"

        else:

            match_level = "low"
            match_label = "Possible Match"

        # ----------------------------------------------------
        # Add match
        # ----------------------------------------------------

        prepared_matches.append(
            {
                "lost_item": lost_item,
                "found_item": found_item,
                "similarity": similarity,
                "score": similarity,
                "match_level": match_level,
                "match_label": match_label
            }
        )

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    return render_template(
        "matches.html",
        matches=prepared_matches
    )


# ============================================================
# /MATCH
# ============================================================

@match_bp.route("/match")
def match_page():

    return redirect(
        url_for("match.matches")
    )