from django.shortcuts import redirect


def redirect_to_schema(request):
    return redirect("redoc")
