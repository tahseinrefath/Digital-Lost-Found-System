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
# LOST BLUEPRINT
# ============================================================

lost_bp = Blueprint("lost", __name__)


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
            FROM lost_items
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
            return user.get("name", "")

    except Exception as error:

        print(
            "Reporter name error:",
            error
        )

    return ""


# ============================================================
# REPORT LOST ITEM
# ============================================================

@lost_bp.route(
    "/report-lost",
    methods=["GET", "POST"]
)
def report_lost():

    # --------------------------------------------------------
    # LOGIN CHECK
    # --------------------------------------------------------

    if not login_required():

        flash(
            "Please login to report a lost item.",
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

        lost_date = request.form.get(
            "lost_date",
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
                url_for("lost.report_lost")
            )

        if not location:

            flash(
                "Please enter the location.",
                "error"
            )

            return redirect(
                url_for("lost.report_lost")
            )

        if not phone:

            flash(
                "Please enter your phone number.",
                "error"
            )

            return redirect(
                url_for("lost.report_lost")
            )

        if not lost_date:

            flash(
                "Please select the lost date.",
                "error"
            )

            return redirect(
                url_for("lost.report_lost")
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
                url_for("lost.report_lost")
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
                    url_for("lost.report_lost")
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
                    url_for("lost.report_lost")
                )

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        user_id = session["user_id"]

        try:

            if has_phone_column(db):

                cursor = db.execute(
                    """
                    INSERT INTO lost_items
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        lost_date,
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
                        'lost'
                    )
                    """,
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        lost_date,
                        description,
                        image_filename,
                        phone
                    )
                )

            else:

                cursor = db.execute(
                    """
                    INSERT INTO lost_items
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        lost_date,
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
                        'lost'
                    )
                    """,
                    (
                        user_id,
                        item_name,
                        category,
                        location,
                        lost_date,
                        description,
                        image_filename
                    )
                )

            cursor.close()

            db.commit()

            flash(
                "Lost item reported successfully.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as error:

            print(
                "Lost item insert error:",
                error
            )

            if image_filename:
                delete_image(
                    image_filename
                )

            flash(
                "Unable to report the lost item.",
                "error"
            )

            return redirect(
                url_for("lost.report_lost")
            )

    # ========================================================
    # GET
    #
    # THIS IS THE IMPORTANT PART:
    # Get the logged-in person's name and send it to
    # report_lost.html as reporter_name.
    # ========================================================

    reporter_name = get_reporter_name(
        db
    )

    return render_template(
        "report_lost.html",
        reporter_name=reporter_name
    )


# ============================================================
# VIEW LOST ITEMS
# ============================================================

@lost_bp.route("/lost-items")
def lost_items():

    db = get_db()

    cursor = db.execute(
        """
        SELECT
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        LEFT JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.status = 'lost'
        ORDER BY lost_items.created_at DESC
        """
    )

    items = cursor.fetchall()

    cursor.close()

    return render_template(
        "dashboard.html",
        lost_items=items
    )


# ============================================================
# EDIT LOST ITEM
# ============================================================

@lost_bp.route(
    "/lost/edit/<int:item_id>",
    methods=["GET", "POST"]
)
def edit_lost(item_id):

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
            lost_items.*,
            users.name AS reporter_name
        FROM lost_items
        LEFT JOIN users
            ON lost_items.user_id = users.id
        WHERE lost_items.id = ?
          AND lost_items.user_id = ?
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
            "Lost item not found.",
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

        lost_date = request.form.get(
            "lost_date",
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
                    "lost.edit_lost",
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
                    "lost.edit_lost",
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
                    "lost.edit_lost",
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
                    "lost.edit_lost",
                    item_id=item_id
                )
            )

        if not lost_date:

            flash(
                "Please select the lost date.",
                "error"
            )

            return redirect(
                url_for(
                    "lost.edit_lost",
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
                        "lost.edit_lost",
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
                        "lost.edit_lost",
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
                    UPDATE lost_items
                    SET
                        item_name = ?,
                        category = ?,
                        location = ?,
                        lost_date = ?,
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
                        lost_date,
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
                    UPDATE lost_items
                    SET
                        item_name = ?,
                        category = ?,
                        location = ?,
                        lost_date = ?,
                        description = ?,
                        image = ?
                    WHERE id = ?
                      AND user_id = ?
                    """,
                    (
                        item_name,
                        category,
                        location,
                        lost_date,
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
                "Lost item updated successfully.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as error:

            print(
                "Lost item update error:",
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
                "Unable to update the lost item.",
                "error"
            )

            return redirect(
                url_for(
                    "lost.edit_lost",
                    item_id=item_id
                )
            )

    # --------------------------------------------------------
    # EDIT PAGE
    # --------------------------------------------------------

    return render_template(
        "edit_lost.html",
        item=item
    )


# ============================================================
# DELETE LOST ITEM
# ============================================================

@lost_bp.route(
    "/lost/delete/<int:item_id>",
    methods=["GET", "POST"]
)
def delete_lost(item_id):

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
        FROM lost_items
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
            "Lost item not found.",
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
            DELETE FROM lost_items
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
            "Lost item deleted successfully.",
            "success"
        )

    except Exception as error:

        print(
            "Lost item delete error:",
            error
        )

        flash(
            "Unable to delete the lost item.",
            "error"
        )

    return redirect(
        url_for("dashboard")
    )