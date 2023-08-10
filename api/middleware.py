from django.utils.deprecation import MiddlewareMixin


class DRFTokenCookieMiddleware(MiddlewareMixin):
    """
    Add auth token from auth_token cookie if there's no authentication header
    """

    def process_request(self, request):
        if "HTTP_AUTHORIZATION" not in request.META:
            access_token = request.COOKIES.get("accessToken", None)
            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
