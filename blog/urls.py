from . import views
from django.urls import path

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('<slug:slug>/', views.post_detail, name='post_detail')
    
]