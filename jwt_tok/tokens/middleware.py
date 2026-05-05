from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.deprecation import MiddlewareMixin

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # user logged in hai session se?
        if request.user.is_authenticated:
            # refresh token lo session se
            refresh_token = request.session.get('refresh_token')
            
            if refresh_token:
                try:
                    # check karo valid hai?
                    token = RefreshToken(refresh_token)
                    # valid hai → kuch mat karo
                except TokenError:
                    # expire ho gaya → logout karo
                    logout(request)  