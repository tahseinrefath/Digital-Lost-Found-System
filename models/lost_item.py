class LostItem:
    """
    Represents a lost item in the Digital Lost & Found System.
    """

    def __init__(
        self,
        id=None,
        user_id=None,
        item_name="",
        category="",
        location="",
        lost_date="",
        description="",
        image=None,
        status="lost",
        created_at=None
    ):
        self.id = id
        self.user_id = user_id
        self.item_name = item_name
        self.category = category
        self.location = location
        self.lost_date = lost_date
        self.description = description
        self.image = image
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        """
        Convert the lost item into a dictionary.
        """

        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "category": self.category,
            "location": self.location,
            "lost_date": self.lost_date,
            "description": self.description,
            "image": self.image,
            "status": self.status,
            "created_at": self.created_at
        }