from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from bot.views import MainBotAPIView
from chats.views import GetUserChatsView, MessageViewSet
from courses.views import UserCoursesAPIView
from faq.views import FAQAPIView
from materials.views import MaterialCheckAPIView
from users.views import UserLoginView, UserLogoutView

messages_router = SimpleRouter()
messages_router.register('messages', MessageViewSet, basename='messages')

api_urls = [
    path('login/', ensure_csrf_cookie(UserLoginView.as_view()), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('chats/', GetUserChatsView.as_view(), name='user_chats'),
    path('faq/<str:course_uuid>/', FAQAPIView.as_view(), name='course_faq'),
    path('courses/', UserCoursesAPIView.as_view(), name='user_courses'),
    path(
        'materials-check/<str:material_check_uuid>/',
        MaterialCheckAPIView.as_view(),
        name='check_material',
    ),
    path('bot/', MainBotAPIView.as_view(), name='bot'),
]

urlpatterns = [
    re_path(r'^webpush/', include('webpush.urls'), name='webpush'),
    path('api/', include(messages_router.urls)),
    path('api/', include((api_urls, 'api'))),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema-ui/', SpectacularSwaggerView.as_view(url_name='schema')),
]
