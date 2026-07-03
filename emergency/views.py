import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings as django_settings
from .models import EmergencyContact, SOSAlert
from .forms import EmergencyContactForm


@login_required
def sos_page(request):
    """Main SOS page with panic button and contact list."""
    contacts = EmergencyContact.objects.filter(user=request.user)
    recent_alerts = SOSAlert.objects.filter(user=request.user)[:5]
    return render(request, 'emergency/sos.html', {
        'contacts': contacts,
        'recent_alerts': recent_alerts,
    })


@login_required
@csrf_exempt
def trigger_sos(request):
    """AJAX endpoint: capture GPS, email all emergency contacts, log event."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method.'}, status=405)

    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        address = data.get('address', 'Location not available')
    except (json.JSONDecodeError, Exception):
        lat, lng, address = None, None, 'Location not available'

    contacts = EmergencyContact.objects.filter(user=request.user)

    if not contacts.exists():
        return JsonResponse({
            'success': False,
            'error': 'No emergency contacts configured. Please add at least one contact.'
        }, status=400)

    # Build map link
    if lat and lng:
        map_link = f"https://www.google.com/maps?q={lat},{lng}"
        location_text = f"Location: {address}\nGoogle Maps: {map_link}"
    else:
        map_link = ''
        location_text = "Location could not be determined."

    user = request.user
    user_name = user.get_full_name() or user.username

    subject = f"🆘 EMERGENCY SOS ALERT from {user_name} — Prana AI"
    message_body = (
        f"⚠️ EMERGENCY SOS ALERT ⚠️\n\n"
        f"{user_name} has triggered an emergency SOS alert.\n\n"
        f"📍 {location_text}\n\n"
        f"📞 Contact: {user.phone_number or 'Not available'}\n"
        f"📧 Email: {user.email}\n\n"
        f"Please reach out to them immediately.\n\n"
        f"— Prana AI Emergency System"
    )

    notified_count = 0
    for contact in contacts:
        try:
            send_mail(
                subject,
                message_body,
                django_settings.DEFAULT_FROM_EMAIL if hasattr(django_settings, 'DEFAULT_FROM_EMAIL') else 'sos@pranaai.com',
                [contact.email],
                fail_silently=True,
            )
            notified_count += 1
        except Exception:
            pass

    # Log the SOS alert
    alert = SOSAlert.objects.create(
        user=user,
        latitude=lat,
        longitude=lng,
        address=address,
        status='sent' if notified_count > 0 else 'failed',
        contacts_notified=notified_count,
        message=message_body,
    )

    return JsonResponse({
        'success': True,
        'alert_id': alert.id,
        'contacts_notified': notified_count,
        'total_contacts': contacts.count(),
        'map_link': map_link,
    })


@login_required
def add_contact(request):
    """Add a new emergency contact."""
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, f'Emergency contact "{contact.name}" added successfully!')
            return redirect('emergency:sos_page')
    else:
        form = EmergencyContactForm()

    return render(request, 'emergency/add_contact.html', {'form': form})


@login_required
def edit_contact(request, pk):
    """Edit an existing emergency contact."""
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contact "{contact.name}" updated successfully!')
            return redirect('emergency:sos_page')
    else:
        form = EmergencyContactForm(instance=contact)

    return render(request, 'emergency/edit_contact.html', {'form': form, 'contact': contact})


@login_required
def delete_contact(request, pk):
    """Delete an emergency contact."""
    contact = get_object_or_404(EmergencyContact, pk=pk, user=request.user)
    if request.method == 'POST':
        name = contact.name
        contact.delete()
        messages.success(request, f'Contact "{name}" deleted.')
        return redirect('emergency:sos_page')

    return render(request, 'emergency/delete_contact.html', {'contact': contact})


@login_required
def sos_history(request):
    """View past SOS alerts."""
    alerts = SOSAlert.objects.filter(user=request.user)
    return render(request, 'emergency/history.html', {'alerts': alerts})
