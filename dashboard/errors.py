from urllib.parse import urlencode, urlparse, urlunparse

from django.contrib import messages
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


def csrf_failure(request, reason=""):
    # A new token is created before returning the user to the same form.
    # The browser restores non-sensitive answers from session storage on that refresh.
    get_token(request)
    messages.warning(request, "Your form was refreshed for security. Your non-sensitive answers have been restored; please enter your password again if needed and submit once more.")
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        parts = list(urlparse(referer))
        query = dict()
        if parts[4]:
            from urllib.parse import parse_qsl
            query.update(parse_qsl(parts[4], keep_blank_values=True))
        query["_form_refresh"] = "1"
        parts[4] = urlencode(query)
        return redirect(urlunparse(parts))
    return redirect("accounts:register")
