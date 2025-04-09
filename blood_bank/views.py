from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    ListView, CreateView, UpdateView, TemplateView
)
from django.urls import reverse_lazy

from .models import BloodBank, Donor, BloodRequest, Donation, BloodInventory
from .forms import (
    DonorRegistrationForm, DonorProfileForm, BloodRequestForm,
    DonationForm, BloodBankForm, UserRegistrationForm
)
from .exceptions import DonationError


class HomeView(TemplateView):
    template_name = 'blood_bank/home.html'


# Authentication
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'blood_bank/login.html')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserRegistrationForm()
    return render(request, 'blood_bank/register.html', {'form': form})


# Donor Views
@login_required
def donor_register(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            messages.success(request, 'Thank you for registering as a donor!')
            return redirect('donor_profile')
    else:
        form = DonorRegistrationForm()
    return render(request, 'blood_bank/donor_registration.html', {'form': form})


class DonorProfileView(LoginRequiredMixin, UpdateView):
    model = Donor
    form_class = DonorProfileForm
    template_name = 'blood_bank/donor_profile.html'
    success_url = reverse_lazy('donor_profile')

    def get_object(self):
        return get_object_or_404(Donor, user=self.request.user)


class DonorListView(ListView):
    model = Donor
    template_name = 'blood_bank/donor_list.html'
    context_object_name = 'donors'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_donors'] = Donor.objects.count()
        return context


# Blood Request
class BloodRequestCreateView(CreateView):
    model = BloodRequest
    form_class = BloodRequestForm
    template_name = 'blood_bank/blood_request_form.html'
    success_url = reverse_lazy('blood_request_list')

    def form_valid(self, form):
        try:
            blood_group = form.cleaned_data['blood_group']
            units_required = form.cleaned_data['units_required']

            available_banks = BloodInventory.get_available_blood_banks(blood_group, units_required)
            if not available_banks.exists():
                messages.warning(
                    self.request,
                    f"No blood banks currently have {units_required} units of {blood_group}."
                )
                form.instance.status = 'pending'
                return super().form_valid(form)

            form.instance.blood_bank = available_banks.first().blood_bank
            messages.success(self.request, "Blood request submitted successfully!")
            return super().form_valid(form)

        except ValueError as e:
            messages.error(self.request, f"Inventory value error: {str(e)}")
        except TypeError as e:
            messages.error(self.request, f"Inventory type error: {str(e)}")
        except Exception as e:
            messages.error(self.request, f"Error loading inventory: {str(e)}")



class BloodRequestListView(ListView):
    model = BloodRequest
    template_name = 'blood_bank/bloodrequest_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return BloodRequest.objects.all().order_by('-request_date')


# Donations
class DonationCreateView(LoginRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'blood_bank/donation_form.html'
    success_url = reverse_lazy('donation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['donor'] = self.request.user.donor
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.donor = self.request.user.donor
            form.instance.blood_group = self.request.user.donor.blood_group
            messages.success(self.request, "Thank you for your donation!")
            return super().form_valid(form)
        except DonationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(form)


class DonationListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = 'blood_bank/donation_list.html'
    context_object_name = 'donations'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Donation.objects.all().order_by('-donation_date')
        return Donation.objects.filter(
            donor=self.request.user.donor
        ).order_by('-donation_date')


# Blood Bank
class BloodBankListView(ListView):
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
