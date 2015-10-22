from functools import wraps
from django.utils.decorators import available_attrs
from django.http import JsonResponse
from dog import models


def apiLoginRequired(viewFunc):
    @wraps(viewFunc, assigned=available_attrs(viewFunc))
    def wrappedView(request, *args, **kwargs):
        if request.user.is_authenticated():
            return viewFunc(request, *args, **kwargs)
        fields = request.GET

        errorMessage = None
        if "HTTP_AUTHORIZATION" in request.META:
            try:
                token = models.Token.objects.get(token=request.META["HTTP_AUTHORIZATION"])
                request.user = token.user
            except models.Token.DoesNotExist:
                errorMessage = "Invalid access_token"
        else:
            errorMessage = "No access_token provided"
        if errorMessage is None:
            return viewFunc(request, *args, **kwargs)
        else:
            return JsonResponse({
                "error": errorMessage,
            })

    return wrappedView
