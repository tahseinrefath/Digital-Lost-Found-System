from datetime import datetime

from config import MATCH_THRESHOLD, MAX_MATCHES
from utils.helpers import normalize_text


# ============================================================
# TEXT SIMILARITY
# ============================================================

def text_similarity(text1, text2):
    """
    Calculate similarity between two text values.

    Returns a score from 0 to 100.
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
    all_words = words1.union(words2)

    if not all_words:
        return 0

    score = (
        len(common_words)
        / len(all_words)
    ) * 100

    return round(score, 2)


# ============================================================
# CATEGORY MATCHING
# ============================================================

def category_similarity(category1, category2):
    """
    Compare two item categories.

    Same category = 100
    Different category = 0
    """

    category1 = normalize_text(category1)
    category2 = normalize_text(category2)

    if not category1 or not category2:
        return 0

    if category1 == category2:
        return 100

    return 0


# ============================================================
# LOCATION MATCHING
# ============================================================

def location_similarity(location1, location2):
    """
    Compare two locations using word similarity.
    """

    return text_similarity(
        location1,
        location2
    )


# ============================================================
# DATE MATCHING
# ============================================================

def date_similarity(date1, date2):
    """
    Compare lost and found dates.

    Same day = 100
    One day apart = 75
    Two days apart = 50
    Three days apart = 25
    More than three days = 0
    """

    if not date1 or not date2:
        return 0

    try:
        first_date = datetime.strptime(
            str(date1),
            "%Y-%m-%d"
        )

        second_date = datetime.strptime(
            str(date2),
            "%Y-%m-%d"
        )

    except ValueError:
        return 0

    difference = abs(
        (first_date - second_date).days
    )

    if difference == 0:
        return 100

    if difference == 1:
        return 75

    if difference == 2:
        return 50

    if difference == 3:
        return 25

    return 0


# ============================================================
# ITEM MATCH SCORE
# ============================================================

def calculate_match_score(lost_item, found_item):
    """
    Calculate the overall similarity score between
    one lost item and one found item.

    The score uses:

    Item name       -> 40%
    Category        -> 20%
    Location        -> 20%
    Description     -> 10%
    Date            -> 10%

    Total = 100%
    """

    # --------------------------------------------------------
    # Item name
    # --------------------------------------------------------

    name_score = text_similarity(
        lost_item["item_name"],
        found_item["item_name"]
    )


    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    category_score = category_similarity(
        lost_item["category"],
        found_item["category"]
    )


    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location_score = location_similarity(
        lost_item["location"],
        found_item["location"]
    )


    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description_score = text_similarity(
        lost_item["description"],
        found_item["description"]
    )


    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    date_score = date_similarity(
        lost_item["lost_date"],
        found_item["found_date"]
    )


    # --------------------------------------------------------
    # Weighted score
    # --------------------------------------------------------

    total_score = (
        (name_score * 0.40)
        + (category_score * 0.20)
        + (location_score * 0.20)
        + (description_score * 0.10)
        + (date_score * 0.10)
    )

    return round(total_score, 2)


# ============================================================
# MATCH LEVEL
# ============================================================

def get_match_level(score):
    """
    Convert a numeric score into a match level.
    """

    if score >= 70:
        return "high"

    if score >= MATCH_THRESHOLD:
        return "medium"

    return "low"


# ============================================================
# FIND MATCHES
# ============================================================

def find_matches(lost_item, found_items):
    """
    Compare one lost item with all found items.

    Only matches that reach MATCH_THRESHOLD are returned.

    Results are sorted from highest score to lowest score.
    """

    matches = []

    for found_item in found_items:

        score = calculate_match_score(
            lost_item,
            found_item
        )

        if score >= MATCH_THRESHOLD:

            matches.append(
                {
                    "lost_id": lost_item["id"],
                    "found_id": found_item["id"],
                    "lost_name": lost_item["item_name"],
                    "lost_category": lost_item["category"],
                    "lost_location": lost_item["location"],
                    "lost_date": lost_item["lost_date"],
                    "lost_description": lost_item["description"],
                    "found_name": found_item["item_name"],
                    "found_category": found_item["category"],
                    "found_location": found_item["location"],
                    "found_date": found_item["found_date"],
                    "found_description": found_item["description"],
                    "score": score,
                    "match_level": get_match_level(score),
                    "image": found_item["image"]
                }
            )


    # --------------------------------------------------------
    # Sort highest score first
    # --------------------------------------------------------

    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    # --------------------------------------------------------
    # Limit number of matches
    # --------------------------------------------------------

    return matches[:MAX_MATCHES]


# ============================================================
# FIND ALL USER MATCHES
# ============================================================

def find_all_matches(lost_items, found_items):
    """
    Find possible matches for multiple lost items.

    Returns one combined list of matches.
    """

    all_matches = []

    for lost_item in lost_items:

        matches = find_matches(
            lost_item,
            found_items
        )

        all_matches.extend(matches)


    # --------------------------------------------------------
    # Sort all matches by score
    # --------------------------------------------------------

    all_matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    return all_matches[:MAX_MATCHES]