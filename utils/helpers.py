import os
import uuid
from pathlib import Path

from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS


# ============================================================
# FILE HELPERS
# ============================================================

def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.

    Example:
        photo.jpg  -> True
        document.pdf -> False
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """
    Generate a safe and unique filename for an uploaded image.

    This prevents two users from accidentally using
    the same filename.
    """

    safe_filename = secure_filename(filename)

    if not safe_filename:
        return None

    extension = Path(safe_filename).suffix.lower()

    unique_name = (
        f"{uuid.uuid4().hex}{extension}"
    )

    return unique_name


def save_uploaded_file(file, upload_folder):
    """
    Validate and save an uploaded image.

    Returns:
        filename if successful
        None if the file is invalid
    """

    if file is None:
        return None

    if not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    filename = generate_unique_filename(
        file.filename
    )

    if filename is None:
        return None

    upload_folder = Path(upload_folder)

    upload_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = upload_folder / filename

    file.save(str(file_path))

    return filename


def delete_uploaded_file(filename, upload_folder):
    """
    Delete an uploaded image if it exists.
    """

    if not filename:
        return False

    upload_folder = Path(upload_folder)

    file_path = upload_folder / filename

    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
            return True

        except OSError:
            return False

    return False


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(value):
    """
    Remove unnecessary spaces from text.

    Example:
        "   Mobile Phone   "
        becomes
        "Mobile Phone"
    """

    if value is None:
        return ""

    return str(value).strip()


def normalize_text(value):
    """
    Convert text into a simple lowercase format.

    This is useful for matching lost and found items.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .lower()
        .strip()
        .split()
    )


# ============================================================
# MATCHING HELPERS
# ============================================================

def calculate_text_similarity(text1, text2):
    """
    Calculate a simple word-based similarity score.

    Returns a percentage from 0 to 100.
    """

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0

    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return 0

    common_words = words1.intersection(words2)

    total_words = words1.union(words2)

    score = (
        len(common_words)
        / len(total_words)
    ) * 100

    return round(score, 2)


def get_match_level(score):
    """
    Convert a similarity score into a readable level.
    """

    if score >= 70:
        return "high"

    if score >= 40:
        return "medium"

    return "low"


# ============================================================
# DATE HELPERS
# ============================================================

def is_valid_date(date_string):
    """
    Check whether a date follows YYYY-MM-DD format.
    """

    from datetime import datetime

    if not date_string:
        return False

    try:
        datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return True

    except ValueError:
        return False