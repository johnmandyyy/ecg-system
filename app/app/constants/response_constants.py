from rest_framework.response import Response as __Response
from rest_framework import status as __STATUS

class __Messages:

    PERMISSION_DENIED_MESSAGE = "Permission Denied."
    INVALID_REQUEST = "Request was invalid."
    VALID = "Accepted."

PERMMISSION_DENIED = __Response(
    {"details": __Messages.PERMISSION_DENIED_MESSAGE}, __STATUS.HTTP_401_UNAUTHORIZED
)

INVALID_REQUEST = __Response(
    {"details": __Messages.INVALID_REQUEST}, __STATUS.HTTP_400_BAD_REQUEST
)
