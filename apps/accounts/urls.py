from django.urls import path
from .views import (
    AddAccount,
    blocked,
    CustomLoginView, 
    CustomPasswordResetView, 
    CustomUserRegistrationView, 
    CustomLogoutView,
    PerformTransfer,
    UserDetail,
    UserDocumentsDetail,
    UserCardHistoryView
)

app_name = "accounts"

urlpatterns = [
    path('blocked', blocked, name="blocked"),
    path('users/<id>/auth/', UserDetail.as_view(), name='user'),
    path('users/<id>/documents/', UserDocumentsDetail.as_view(), name='documents'),
    path('cards/<id>/', UserCardHistoryView.as_view(), name='card'),
    path('add-account/', AddAccount.as_view(), name='add_account'),
    path('transfers/', PerformTransfer.as_view(), name='transfer'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('reset_password/', CustomPasswordResetView.as_view(), name='password_reset'),
]
