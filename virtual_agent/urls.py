from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from chats.views import MessageViewSet
from users.views import UserLoginView, UserLogoutView

messages_router = SimpleRouter()
messages_router.register('message', MessageViewSet, basename='message')

api_urls = [
    path('login/', ensure_csrf_cookie(UserLoginView.as_view()), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
]

urlpatterns = [
    path('', include(messages_router.urls)),
    path('api/', include((api_urls, 'api'))),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
]
