from . import views
from django.urls import include, path
from rest_framework import routers

# app_name = 'blog'

router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('api/', include(router.urls), name='api'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('<slug:slug>/', views.post_detail, name='post_detail')
    
]