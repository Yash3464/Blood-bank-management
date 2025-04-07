from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Donor URLs
    path('donor/register/', views.donor_register, name='donor_register'),
    path('profile/', views.DonorProfileView.as_view(), name='donor_profile'),
    path('donors/', views.DonorListView.as_view(), name='donor_list'),
    
    # Blood Request URLs
    path('request/new/', views.BloodRequestCreateView.as_view(), name='blood_request_create'),
    path('requests/', views.BloodRequestListView.as_view(), name='blood_request_list'),
    
    # Donation URLs
    path('donate/', views.DonationCreateView.as_view(), name='donation_create'),
    path('donations/', views.DonationListView.as_view(), name='donation_list'),
    
    # Blood Bank URLs
    path('banks/', views.BloodBankListView.as_view(), name='blood_bank_list'),
] 