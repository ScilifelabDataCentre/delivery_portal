"""Authentication related functions/tools."""

####################################################################################################
# IMPORTS ################################################################################ IMPORTS #
####################################################################################################

# Installed
import datetime
import argon2
import http
import flask
import json
import jwcrypto
from jwcrypto import jwk, jwt
import structlog

# Own modules
from dds_web.errors import AuthenticationError, AccessDeniedError
from dds_web.database import models
from dds_web import basic_auth, auth
import dds_web.utils
from dds_web import mail

action_logger = structlog.getLogger("actions")

# VARIABLES ############################################################################ VARIABLES #

MFA_EXPIRES_IN = datetime.timedelta(hours=48)

####################################################################################################
# FUNCTIONS ############################################################################ FUNCTIONS #
####################################################################################################


@basic_auth.error_handler
def auth_error(status):
    return auth_error_common(status)


@auth.error_handler
def auth_error(status):
    return auth_error_common(status)


def auth_error_common(status):
    if status == http.HTTPStatus.UNAUTHORIZED:
        raise AuthenticationError()
    elif status == http.HTTPStatus.FORBIDDEN:
        raise AccessDeniedError(message="Insufficient credentials")


@basic_auth.get_user_roles
def get_user_roles(user):
    return get_user_roles_common(user)


@auth.get_user_roles
def get_user_roles(user):
    return get_user_roles_common(user)


def get_user_roles_common(user):
    """Return the users role as saved in the db."""

    return user.role


def verify_general_token(token):
    """Verifies the format, signature and expiration time of an encrypted and signed JWT token.
    Raises ValueError if token is invalid, could raise other exceptions from dependencies.

    If user given by the "sub" claim is found in the database it returns
    (user, claims)

    Where claims is a dictionary of the token claims.

    If the user is not found in the database, it returns
    (None, claims)
    """
    try:
        data = (
            verify_token_signature(token)
            if token.count(".") == 2
            else decrypt_and_verify_token_signature(token)
        )
    except (ValueError, jwcrypto.common.JWException) as e:
        # ValueError is raised when the token doesn't look right (for example no periods)
        # jwcryopto.common.JWException is the base exception raised by jwcrypto,
        # and is raised when the token is malformed or invalid.
        flask.current_app.logger.exception(e)
        raise AuthenticationError(message="Invalid token")

    expiration_time = data.get("exp")
    # we use a hard check on top of the one from the dependency
    # exp shouldn't be before now no matter what
    if expiration_time and (
        dds_web.utils.current_time() <= datetime.datetime.fromtimestamp(expiration_time)
    ):
        username = data.get("sub")
        user = models.User.query.get(username) if username else None
        return user, data
    raise AuthenticationError(message="Expired token")


@auth.verify_token
def verify_token(token):
    user, data = verify_general_token(token)
    return handle_multi_factor_authentication(user, data.get("mfa_auth_time"))


def handle_multi_factor_authentication(user, mfa_auth_time_string):
    if user:
        if mfa_auth_time_string:
            mfa_auth_time = datetime.datetime.fromtimestamp(mfa_auth_time_string)
            if mfa_auth_time >= dds_web.utils.current_time() - MFA_EXPIRES_IN:
                return user

        send_hotp_email(user)

        if flask.request.path.endswith("/user/second_factor"):
            return user

        raise AuthenticationError(
            message="Two-factor authentication is required! Please check your primary e-mail!"
        )
    return None


def send_hotp_email(user):
    if not user.hotp_issue_time or (
        user.hotp_issue_time
        and (dds_web.utils.current_time() - user.hotp_issue_time > datetime.timedelta(minutes=15))
    ):
        hotp_value = user.generate_HOTP_token()
        msg = dds_web.utils.create_one_time_password_email(user, hotp_value)
        mail.send(msg)
        return True
    return False


def extract_encrypted_token_content(token, username):
    """Extract the sensitive content from inside the encrypted token"""
    content = decrypt_and_verify_token_signature(token)
    return content.get("sen_con") if content.get("sub") == username else None


def decrypt_and_verify_token_signature(token):
    """Wrapper function that streamlines decryption and signature verification,
    and returns the claims"""
    return verify_token_signature(decrypt_token(token))


def decrypt_token(token):
    """Decrypt the encrypted token and return
    the signed token embedded inside"""
    key = jwk.JWK.from_password(flask.current_app.config.get("SECRET_KEY"))
    decrypted_token = jwt.JWT(key=key, jwt=token)
    return decrypted_token.claims


def verify_token_signature(token):
    """Verify the signature of the token and return the claims
    such as subject/username on valid signature"""
    key = jwk.JWK.from_password(flask.current_app.config.get("SECRET_KEY"))
    try:
        jwttoken = jwt.JWT(key=key, jwt=token, algs=["HS256"])
        return json.loads(jwttoken.claims)
    except jwt.JWTExpired:
        # jwt dependency uses a 60 seconds leeway to check exp
        # it also prints out a stack trace for it, so we handle it here
        raise AuthenticationError(message="Expired token")


@basic_auth.verify_password
def verify_password(username, password):
    """Verify that user exists and that password is correct."""
    user = models.User.query.get(username)
    if user and user.verify_password(input_password=password):
        send_hotp_email(user)
        return user
    return None
