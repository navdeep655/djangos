from functools import wraps
from rest_framework_simplejwt .tokens import AccessToken
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from functools import wraps
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


def jwt_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):

        access_token = request.COOKIES.get("access_token")

        # -------------------------
        # 1. Try access token first
        # -------------------------
        if access_token:
            try:
                decoded = AccessToken(access_token)
                user_id = decoded["user_id"]
                request.user = User.objects.get(id=user_id)
                return func(request, *args, **kwargs)

            except Exception:
                pass  # access expired → go to refresh

        # -------------------------
        # 2. Try refresh token
        # -------------------------
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return redirect("authlogin")

        try:
            refresh = RefreshToken(refresh_token)

            new_access = str(refresh.access_token)
            user_id = refresh["user_id"]

            request.user = User.objects.get(id=user_id)

            response = func(request, *args, **kwargs)

            response.set_cookie(
                "access_token",
                new_access,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response

        except Exception:
            response = redirect('authlogin')
            response.delete_cookie('access_token', path='/')   
            response.delete_cookie('refresh_token', path='/') 
            return response

    return wrapper