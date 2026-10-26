class User:
    """
    Represents a user in the Digital Lost & Found System.
    """

    def __init__(
        self,
        id=None,
        name="",
        email="",
        password="",
        created_at=None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.created_at = created_at

    def to_dict(self):
        """
        Convert the user into a dictionary.
        """

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at
        }