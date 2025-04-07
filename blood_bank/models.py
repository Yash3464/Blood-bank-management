from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from .exceptions import *

# Regular expression validators
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

email_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message="Enter a valid email address."
)

class BloodGroup:
    """Class to handle blood group related operations"""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    @classmethod
    def validate_blood_group(cls, blood_group):
        valid_groups = [group[0] for group in cls.BLOOD_GROUPS]
        if blood_group not in valid_groups:
            raise InvalidBloodGroupError(f"Invalid blood group: {blood_group}")
        return blood_group

class BloodBank(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(
        max_length=15,
        validators=[phone_regex]
    )
    email = models.EmailField(validators=[email_regex])

    def __str__(self):
        return self.name

    def get_total_inventory(self):
        """Get total blood units available in the blood bank"""
        try:
            return sum(inv.units_available for inv in self.bloodinventory_set.all())
        except Exception as e:
            raise BloodBankError(f"Error calculating inventory: {str(e)}")

    class Meta:
        verbose_name = "Blood Bank"
        verbose_name_plural = "Blood Banks"

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, validators=[phone_regex])
    age = models.IntegerField(default=18)
    blood_type = models.CharField(max_length=3, choices=BLOOD_GROUPS, default='O+')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.blood_type})"

    class Meta:
        ordering = ['-created_at']

class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.BLOOD_GROUPS)
    units_donated = models.IntegerField(validators=[MinValueValidator(1)])
    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor} - {self.units_donated} units on {self.donation_date.date()}"

    def save(self, *args, **kwargs):
        """Override save to validate donation and update inventory"""
        try:
            if not self.donor.can_donate():
                raise DonationError("Donor is not eligible to donate yet")

            BloodGroup.validate_blood_group(self.blood_group)
            
            # Create the donation record
            super().save(*args, **kwargs)

            # Update inventory
            inventory, created = BloodInventory.objects.get_or_create(
                blood_bank=self.blood_bank,
                blood_group=self.blood_group,
                defaults={'units_available': 0}
            )
            inventory.units_available += self.units_donated
            inventory.save()

            # Update donor's last donation date
            self.donor.last_donation_date = timezone.now().date()
            self.donor.save()

        except Exception as e:
            raise DonationError(f"Error processing donation: {str(e)}")

class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]

    requester_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.BLOOD_GROUPS)
    units_required = models.IntegerField(validators=[MinValueValidator(1)])
    hospital_name = models.CharField(max_length=100)
    hospital_address = models.TextField()
    contact_number = models.CharField(max_length=15, validators=[phone_regex])
    email = models.EmailField(validators=[email_regex])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.requester_name} - {self.blood_group} ({self.status})"

    def approve_request(self):
        """Approve blood request if sufficient units are available"""
        try:
            if not self.blood_bank:
                raise BloodRequestError("No blood bank assigned to this request")

            inventory = BloodInventory.objects.get(
                blood_bank=self.blood_bank,
                blood_group=self.blood_group
            )

            if inventory.units_available < self.units_required:
                raise InsufficientBloodUnitsError(
                    f"Only {inventory.units_available} units available"
                )

            inventory.units_available -= self.units_required
            inventory.save()
            
            self.status = 'approved'
            self.save()
            
        except BloodInventory.DoesNotExist:
            raise BloodRequestError(f"No inventory found for blood group {self.blood_group}")
        except Exception as e:
            raise BloodRequestError(f"Error processing request: {str(e)}")

class BloodInventory(models.Model):
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.BLOOD_GROUPS)
    units_available = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_bank} - {self.blood_group}: {self.units_available} units"

    class Meta:
        verbose_name = "Blood Inventory"
        verbose_name_plural = "Blood Inventories"
        unique_together = ['blood_bank', 'blood_group']

    @classmethod
    def get_available_blood_banks(cls, blood_group, units_required):
        """Find blood banks with sufficient units of required blood group"""
        try:
            return cls.objects.filter(
                blood_group=blood_group,
                units_available__gte=units_required
            ).select_related('blood_bank')
        except Exception as e:
            raise BloodBankError(f"Error finding available blood banks: {str(e)}")
