"""Testing of the dds_web code with pytest."""

from base64 import b64encode

# Copied from dds_cli __init__.py:

__all__ = [
    "DDS_METHODS",
    "DDS_DIR_REQUIRED_METHODS",
    "DDS_PROJ_REQUIRED_METHODS",
    "DDS_PROJ_NOT_REQUIRED_METHODS",
    "USER_CREDENTIALS",
    "UserAuth",
    "DDSEndpoint",
]


###############################################################################
# VARIABLES ####################################################### VARIABLES #
###############################################################################

# Keep track of all allowed methods
DDS_METHODS = ["put", "get", "ls", "rm"]

# Methods to which a directory created by DDS
DDS_DIR_REQUIRED_METHODS = ["put", "get"]

# Methods which require a project ID
DDS_PROJ_REQUIRED_METHODS = ["put", "get"]

# Methods which do not require a project ID
DDS_PROJ_NOT_REQUIRED_METHODS = ["ls", "rm"]

# The credentials used for the tests
USER_CREDENTIALS = {
    "empty": ":",
    "nouser": ":password",
    "nopassword": "username:",
    "wronguser": "scriptkiddie:password",
    "researcher": "username:password",
    "researcher": "username:password",
    "admin": "admin:password",
    "admin2": "admin2:password",
}

###############################################################################
# CLASSES ########################################################### CLASSES #
###############################################################################
class UserAuth:
    """A helper class that can return the credentials in various forms as required for the API."""

    def __init__(self, credentials):
        self.credentials = credentials

    # class can be extended by various means to act on the credentials

    def plain(self):
        return self.credentials

    def as_tuple(self):
        return tuple(self.credentials.split(":"))

    def basic(self):
        return b64encode(self.credentials.encode("utf-8")).decode("utf-8")

    def post_headers(self):
        return {"Authorization": f"Basic {self.basic()}"}

    def token(self, client):

        response = client.get(DDSEndpoint.TOKEN, auth=(self.as_tuple()))

        # Get response from api
        response_json = response.json
        token = response_json.get("token")

        return {"Authorization": f"Bearer {token}"}


class DDSEndpoint:
    """Defines all DDS urls."""

    # Base url - local or remote
    BASE_ENDPOINT = "/api/v1"

    # User creation
    USER_INVITE = BASE_ENDPOINT + "/user/invite"

    # Authentication - user and project
    TOKEN = BASE_ENDPOINT + "/user/token"

    # S3Connector keys
    S3KEYS = BASE_ENDPOINT + "/s3/proj"

    # File related urls
    FILE_NEW = BASE_ENDPOINT + "/file/new"
    FILE_MATCH = BASE_ENDPOINT + "/file/match"
    FILE_INFO = BASE_ENDPOINT + "/file/info"
    FILE_INFO_ALL = BASE_ENDPOINT + "/file/all/info"
    FILE_UPDATE = BASE_ENDPOINT + "/file/update"

    # Project specific urls
    PROJECT_SIZE = BASE_ENDPOINT + "/proj/size"
    PROJECT_CREATE = BASE_ENDPOINT + "/proj/create"

    # Listing urls
    LIST_PROJ = BASE_ENDPOINT + "/proj/list"
    LIST_FILES = BASE_ENDPOINT + "/files/list"

    # Deleting urls
    REMOVE_PROJ_CONT = BASE_ENDPOINT + "/proj/rm"
    REMOVE_FILE = BASE_ENDPOINT + "/file/rm"
    REMOVE_FOLDER = BASE_ENDPOINT + "/file/rmdir"

    # Encryption keys
    PROJ_PUBLIC = BASE_ENDPOINT + "/proj/public"
    PROJ_PRIVATE = BASE_ENDPOINT + "/proj/private"

    # Display facility usage
    USAGE = BASE_ENDPOINT + "/usage"
    INVOICE = BASE_ENDPOINT + "/invoice"

    TIMEOUT = 5
