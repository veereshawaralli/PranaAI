from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def map_view(request):
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    return render(request, 'locator/map.html', {'google_maps_api_key': api_key})
