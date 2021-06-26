class Suggestion:
    """
    Object containing the data to suggest
    """

    def __init__(
        self, email_address, name, content,
    ):
        self.email_address = email_address
        self.name = name
        self.content = content

    def __hash__(self):
        return hash((self.email_address, self.name, self.content,))

    def __eq__(self, other):
        return (
            self.email_address == other.email_address
            and self.name == other.name
            and self.content == other.content
        )

    def __repr__(self):
        return f"Suggestion({self.email_address}, {self.name}, {self.content})"
