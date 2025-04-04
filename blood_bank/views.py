from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from .models import BloodBank, Donor, BloodRequest, Donation, BloodInventory
from .forms import (
    DonorRegistrationForm, DonorProfileForm, BloodRequestForm,
    DonationForm, BloodBankForm, UserRegistrationForm
)
from .exceptions import *

class HomeView(TemplateView):
    """Home page view"""
    template_name = 'blood_bank/home.html'

# User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'blood_bank/register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'blood_bank/login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Donor Registration
@login_required
def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            return redirect('profile')
    else:
        form = DonorRegistrationForm()
    return render(request, 'blood_bank/donor_register.html', {'form': form})

# Blood Request
@login_required
def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BloodRequestForm()
    return render(request, 'blood_bank/request_blood.html', {'form': form})

# Blood Bank List
def blood_banks(request):
    banks = BloodBank.objects.all()
    return render(request, 'blood_bank/blood_banks.html', {'banks': banks})

# User Profile
@login_required
def profile(request):
    donor = Donor.objects.filter(user=request.user).first()
    return render(request, 'blood_bank/profile.html', {'donor': donor})

def donor_register(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new donor
            Donor.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                age=form.cleaned_data['age'],
                blood_type=form.cleaned_data['blood_type']
            )
            messages.success(request, 'Thank you for registering as a donor!')
            return redirect('home')
    else:
        form = DonorRegistrationForm()
    
    return render(request, 'blood_bank/donor_registration.html', {'form': form})

class DonorRegistrationView(CreateView):
    model = Donor
    form_class = DonorRegistrationForm
    template_name = 'blood_bank/donor_registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, 'Thank you for registering as a donor!')
        return super().form_valid(form)

class DonorProfileView(LoginRequiredMixin, UpdateView):
    """View for updating donor profile"""
    model = Donor
    form_class = DonorProfileForm
    template_name = 'blood_bank/donor_profile.html'
    success_url = reverse_lazy('donor_profile')

    def get_object(self):
        return get_object_or_404(Donor, user=self.request.user)

class BloodRequestCreateView(SuccessMessageMixin, CreateView):
    """View for creating blood requests"""
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = 'blood_bank/blood_request_form.html'
    success_url = reverse_lazy('blood_request_list')
    success_message = "Blood request submitted successfully!"

    def form_valid(self, form):
        try:
            # Find suitable blood banks
            blood_group = form.cleaned_data['blood_group']
            units_required = form.cleaned_data['units_required']
            
            available_banks = BloodInventory.get_available_blood_banks(
                blood_group, units_required
            )

            if not available_banks.exists():
                messages.warning(
                    self.request,
                    f"No blood banks currently have {units_required} units of {blood_group} available."
                )
                # Save the request anyway with pending status
                form.instance.status = 'pending'
                return super().form_valid(form)

            # Assign to the first available blood bank
            form.instance.blood_bank = available_banks.first().blood_bank
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class DonationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating donations"""
    model = Donation
    form_class = DonationForm
    template_name = 'blood_bank/donation_form.html'
    success_url = reverse_lazy('donation_list')
    success_message = "Thank you for your donation!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['donor'] = self.request.user.donor
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.donor = self.request.user.donor
            form.instance.blood_group = self.request.user.donor.blood_group
            return super().form_valid(form)
        except DonationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(form)

class BloodBankListView(ListView):
    """View for listing blood banks"""
    model = BloodBank
    template_name = 'blood_bank/bloodbank_list.html'
    context_object_name = 'blood_banks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            for bank in context['blood_banks']:
                bank.total_inventory = bank.get_total_inventory()
        except Exception as e:
            messages.error(self.request, f"Error loading inventory: {str(e)}")
        return context

class BloodRequestListView(ListView):
    """View for listing blood requests"""
    model = BloodRequest
    template_name = 'blood_bank/bloodrequest_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        """Get all blood requests ordered by most recent first"""
        return BloodRequest.objects.all().order_by('-request_date')

class DonationListView(LoginRequiredMixin, ListView):
    """View for listing donations"""
    model = Donation
    template_name = 'blood_bank/donation_list.html'
    context_object_name = 'donations'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Donation.objects.all().order_by('-donation_date')
        return Donation.objects.filter(
            donor=self.request.user.donor
        ).order_by('-donation_date')

def home(request):
    return render(request, 'blood_bank/home.html')

# Donor List View
class DonorListView(ListView):
    """View for listing all registered donors"""
    model = Donor
    template_name = 'blood_bank/donor_list.html'
    context_object_name = 'donors'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_donors'] = Donor.objects.count()
        return context
