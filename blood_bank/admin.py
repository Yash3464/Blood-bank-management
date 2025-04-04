from django.contrib import admin
from .models import BloodBank, Donor, BloodInventory, BloodRequest, Donation

@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email')
    search_fields = ('name', 'email')

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age', 'blood_type', 'created_at')
    list_filter = ('blood_type', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)

@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ('blood_bank', 'blood_group', 'units_available', 'last_updated')
    list_filter = ('blood_bank', 'blood_group')
    search_fields = ('blood_bank__name',)

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('requester_name', 'blood_group', 'units_required', 'status', 'request_date')
    list_filter = ('status', 'blood_group')
    search_fields = ('requester_name', 'hospital_name')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'blood_bank', 'blood_group', 'units_donated', 'donation_date')
    list_filter = ('blood_bank', 'blood_group')
    search_fields = ('donor__name', 'blood_bank__name')
