class AuthenticationError(Exception):
    """Errors due to user authentication.

    Return the message with Rich no-entry-sign emoji either side.
    """

    def __str__(self):
        return f":no_entry_sign: {self.args[0]} :no_entry_sign:"
