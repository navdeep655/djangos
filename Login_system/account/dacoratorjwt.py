from functools import wraps
from rest_framework_simplejwt .tokens import AccessToken
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User=get_user_model()

def jwt_required(func):
    @wraps(func)
    def wrapper(request,*args,**kwargs):
        token=request.COOKIES.get("access_token")
        print(token)

        if not token:
            return redirect("login")
        try:
            decoded = AccessToken(token)
            user_id = decoded['user_id']

            request.user = User.objects.get(id=user_id)

        except Exception as e:
            print("JWT ERROR:", e)
            return redirect('login')

        return func(request, *args, **kwargs)

    return wrapper
