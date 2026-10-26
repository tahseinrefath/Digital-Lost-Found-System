from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.utils import secure_filename
from pathlib import Path
import uuid

from database.db import get_db
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


# ============================================================
# FOUND BLUEPRINT
# ============================================================

found_bp = Blueprint("found", __name__)


# ============================================================
# LOGIN CHECK
# ============================================================

def login_required():
    return "user_id" in session


# ============================================================
# IMAGE VALIDATION
# ============================================================

def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# SAVE IMAGE
# ============================================================

def save_image(file):

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    Path(UPLOAD_FOLDER).mkdir(
        parents=True,
        exist_ok=True
    )

    original_name = secure_filename(
        file.filename
    )

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )

    file_path = Path(
        UPLOAD_FOLDER
    ) / filename

    file.save(
        str(file_path)
    )

    return filename


# ============================================================
# DELETE IMAGE
# ============================================================

def delete_image(filename):

    if not filename:
        return

    try:

        file_path = (
            Path(UPLOAD_FOLDER)
            / filename
        )

        if file_path.exists():
            file_path.unlink()

    except Exception as error:

        print(
            "Image delete error:",
            error
        )


# ============================================================
# CHECK PHONE COLUMN
# ============================================================

def has_phone_column(db):

    try:

        cursor = db.execute(
            """
            SHOW COLUMNS
            FROM found_items
            LIKE 'phone'
            """
        )

        result = cursor.fetchone()

        cursor.close()

        return result is not None

    except Exception as error:

        print(
            "Phone column check error:",
            error
        )

        return False


# ============================================================
# GET REPORTER NAME
# ============================================================

def get_reporter_name(db):

    user_id = session.get("user_id")

    if not user_id:
        return ""

    try:

        cursor = db.execute(
            """
            SELECT name
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        cursor.close()

        if user:
            return user.get(
                "name",
                ""
            )

    except Exception as error:

        print(
            "Reporter name error:",
            error
        )

    return ""


# ============================================================
# REPORT FOUND ITEM
# ============================================================

@found_bp.route(
    "/report-found",
    methods=["GET", "POST"]
)
def report_found():

    # --------------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------------

    if not login_required():

        flash(
            "Please login to report a found item.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    db = get_db()

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        found_date = request.form.get(
            "found_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        image_file = request.files.get(
            "image"
        )

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        if not item_name:

            flash(
                "Please enter the item name.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

        if not location:

            flash(
                "Please enter the location.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

        if not phone:

            flash(
                "Please enter your phone number.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

        if not found_date:

            flash(
                "Please select the found date.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

        # ----------------------------------------------------
        # PHONE VALIDATION
        # ----------------------------------------------------

        if not phone.isdigit() or len(phone) != 10:

            flash(
                "Please enter a valid 10-digit phone number.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_filename = None

        if image_file and image_file.filename:

            if not allowed_file(
                image_file.filename
            ):

                flash(
                    "Invalid image format. Use JPG, JPEG, PNG, GIF or WEBP.",
                    "error"
                )

                return redirect(
                    url_for("found.report_found")
                )

            image_filename = save_image(
                image_file
            )

            if not image_filename:

                flash(
                    "Unable to upload the image.",
                    "error"
                )

                return redirect(
                    url_for("found.report_found")
                )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        user_id = session["user_id"]

        try:

            if has_phone_column(db):

                cursor = db.execute(
                    """
                    INSERT INTO found_items
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        image,
                        phone,
                        status
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        'found'
                    )
                    """,
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        image_filename,
                        phone
                    )
                )

            else:

                cursor = db.execute(
                    """
                    INSERT INTO found_items
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        image,
                        status
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        'found'
                    )
                    """,
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        image_filename
                    )
                )

            cursor.close()

            db.commit()

            flash(
                "Found item reported successfully.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as error:

            print(
                "Found item insert error:",
                error
            )

            if image_filename:
                delete_image(
                    image_filename
                )

            flash(
                "Unable to report the found item.",
                "error"
            )

            return redirect(
                url_for("found.report_found")
            )

    # ========================================================
    # GET
    #
    # IMPORTANT:
    # Get the logged-in person's name and send it to
    # report_found.html as reporter_name.
    # ========================================================

    reporter_name = get_reporter_name(
        db
    )

    return render_template(
        "report_found.html",
        reporter_name=reporter_name
    )


# ============================================================
# VIEW ALL FOUND ITEMS
# ============================================================

@found_bp.route("/found-items")
def found_items():

    db = get_db()

    cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        LEFT JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.status = 'found'
        ORDER BY found_items.created_at DESC
        """
    )

    items = cursor.fetchall()

    cursor.close()

    return render_template(
        "dashboard.html",
        found_items=items
    )


# ============================================================
# EDIT FOUND ITEM
# ============================================================

@found_bp.route(
    "/found/edit/<int:item_id>",
    methods=["GET", "POST"]
)
def edit_found(item_id):

    if not login_required():

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    db = get_db()

    user_id = session["user_id"]

    # --------------------------------------------------------
    # GET ITEM
    # --------------------------------------------------------

    cursor = db.execute(
        """
        SELECT
            found_items.*,
            users.name AS reporter_name
        FROM found_items
        LEFT JOIN users
            ON found_items.user_id = users.id
        WHERE found_items.id = ?
          AND found_items.user_id = ?
        LIMIT 1
        """,
        (
            item_id,
            user_id
        )
    )

    item = cursor.fetchone()

    cursor.close()

    if not item:

        flash(
            "Found item not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        found_date = request.form.get(
            "found_date",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        image_file = request.files.get(
            "image"
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not item_name:

            flash(
                "Please enter the item name.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

        if not location:

            flash(
                "Please enter the location.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

        if not phone:

            flash(
                "Please enter your phone number.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

        if not phone.isdigit() or len(phone) != 10:

            flash(
                "Please enter a valid 10-digit phone number.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

        if not found_date:

            flash(
                "Please select the found date.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        old_image = item.get(
            "image"
        )

        new_image = old_image

        if image_file and image_file.filename:

            if not allowed_file(
                image_file.filename
            ):

                flash(
                    "Invalid image format.",
                    "error"
                )

                return redirect(
                    url_for(
                        "found.edit_found",
                        item_id=item_id
                    )
                )

            uploaded_image = save_image(
                image_file
            )

            if not uploaded_image:

                flash(
                    "Unable to upload the new image.",
                    "error"
                )

                return redirect(
                    url_for(
                        "found.edit_found",
                        item_id=item_id
                    )
                )

            new_image = uploaded_image

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        try:

            if has_phone_column(db):

                cursor = db.execute(
                    """
                    UPDATE found_items
                    SET
                        item_name = ?,
                        category = ?,
                        location = ?,
                        found_date = ?,
                        description = ?,
                        image = ?,
                        phone = ?
                    WHERE id = ?
                      AND user_id = ?
                    """,
                    (
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        new_image,
                        phone,
                        item_id,
                        user_id
                    )
                )

            else:

                cursor = db.execute(
                    """
                    UPDATE found_items
                    SET
                        item_name = ?,
                        category = ?,
                        location = ?,
                        found_date = ?,
                        description = ?,
                        image = ?
                    WHERE id = ?
                      AND user_id = ?
                    """,
                    (
                        item_name,
                        category,
                        location,
                        found_date,
                        description,
                        new_image,
                        item_id,
                        user_id
                    )
                )

            cursor.close()

            db.commit()

            if (
                new_image != old_image
                and old_image
            ):

                delete_image(
                    old_image
                )

            flash(
                "Found item updated successfully.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as error:

            print(
                "Found item update error:",
                error
            )

            if (
                new_image != old_image
                and new_image
            ):

                delete_image(
                    new_image
                )

            flash(
                "Unable to update the found item.",
                "error"
            )

            return redirect(
                url_for(
                    "found.edit_found",
                    item_id=item_id
                )
            )

    # --------------------------------------------------------
    # EDIT PAGE
    # --------------------------------------------------------

    return render_template(
        "edit_found.html",
        item=item
    )


# ============================================================
# DELETE FOUND ITEM
# ============================================================

@found_bp.route(
    "/found/delete/<int:item_id>",
    methods=["GET", "POST"]
)
def delete_found(item_id):

    if not login_required():

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    db = get_db()

    user_id = session["user_id"]

    # --------------------------------------------------------
    # GET IMAGE
    # --------------------------------------------------------

    cursor = db.execute(
        """
        SELECT image
        FROM found_items
        WHERE id = ?
          AND user_id = ?
        LIMIT 1
        """,
        (
            item_id,
            user_id
        )
    )

    item = cursor.fetchone()

    cursor.close()

    if not item:

        flash(
            "Found item not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    image_filename = item.get(
        "image"
    )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    try:

        cursor = db.execute(
            """
            DELETE FROM found_items
            WHERE id = ?
              AND user_id = ?
            """,
            (
                item_id,
                user_id
            )
        )

        cursor.close()

        db.commit()

        if image_filename:

            delete_image(
                image_filename
            )

        flash(
            "Found item deleted successfully.",
            "success"
        )

    except Exception as error:

        print(
            "Found item delete error:",
            error
        )

        flash(
            "Unable to delete the found item.",
            "error"
        )

    return redirect(
        url_for("dashboard")
    )