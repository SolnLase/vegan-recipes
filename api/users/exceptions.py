from rest_framework.exceptions import APIException


class PasswordsDoNotMatch(APIException):
    status_code = 400
    default_detail = "The passwords provided do not match."
    default_code = "passwords_do_not_match"


class PasswordTooWeak(APIException):
    status_code = 400
    default_detail = """This password is too weak! Cosider making it at least 8 letters long, 
                        adding upper-case and lower case letters, and numbers"""
    default_code = "password_too_weak"


class WrongToken(APIException):
    status_code = 404
    default_detail = "The token was not found"
    default_code = "token_not_found"
