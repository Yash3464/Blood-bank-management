from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from .exceptions import (
    BloodBankError, DonorNotFoundError, InsufficientBloodUnitsError,
    BloodRequestError, InvalidBloodGroupError, DonationError
)

class BloodBankExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Handle custom exceptions and provide appropriate responses"""
        if isinstance(exception, (BloodBankError, DonorNotFoundError,
                                InsufficientBloodUnitsError, BloodRequestError,
                                InvalidBloodGroupError, DonationError)):
            
            messages.error(request, str(exception))
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(exception)
                }, status=400)
            
            # Redirect back to the previous page
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Let Django handle other exceptions
        return None 