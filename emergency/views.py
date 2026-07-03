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

    # Build map link using OpenStreetMap
    if lat and lng:
        map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=16/{lat}/{lng}"
        location_text = f"Location: {address}\nOpenStreetMap: {map_link}"
    else:
        map_link = ''
        location_text = "Location could not be determined."

    user = request.user
    user_name = user.get_full_name() or user.username

    subject = f"🚨 URGENT: SOS Help Needed from {user_name} 🚨"
    message_body = (
        f"*** URGENT MEDICAL/SAFETY ALERT ***\n\n"
        f"{user_name} has activated their SOS panic button and requires immediate assistance!\n\n"
        f"📍 Location Information:\n{location_text}\n\n"
        f"📞 Phone: {user.phone_number or 'Not available'}\n"
        f"📧 Email: {user.email}\n\n"
        f"Please try to contact them right away. If they do not respond, consider contacting local authorities.\n\n"
        f"Sent automatically via Prana AI Safety System"
    )

    phone_display = user.phone_number or 'Not available'
    map_html = f'<a href="{map_link}" style="display: inline-block; background-color: #dc2626; color: white; text-decoration: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; margin-top: 10px; margin-bottom: 20px;">View Location on Map</a>' if map_link else ''
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
            <div style="background-color: #dc2626; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px; color: white;">🚨 EMERGENCY SOS ALERT 🚨</h1>
            </div>
            <div style="padding: 30px; color: #334155;">
                <div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 4px; margin-bottom: 25px;">
                    <p style="margin: 0; color: #991b1b; font-weight: 600; font-size: 16px;">URGENT: {user_name} requires immediate assistance!</p>
                </div>
                
                <p style="font-size: 16px; line-height: 1.5; margin-bottom: 25px;">
                    You are receiving this message because you are listed as an emergency contact for <strong style="color:#0f172a;">{user_name}</strong>. They have activated their SOS panic button.
                </p>

                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; color: #64748b; font-size: 12px; text-transform: uppercase; margin-bottom: 5px;">📍 Last Known Location</div>
                    <p style="font-size: 16px; margin: 0 0 10px 0; color: #0f172a; font-weight: 500;">{address}</p>
                    {map_html}
                </div>

                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; color: #64748b; font-size: 12px; text-transform: uppercase; margin-bottom: 5px;">📞 Phone Number</div>
                    <p style="font-size: 16px; margin: 0; color: #0f172a; font-weight: 500;">{phone_display}</p>
                </div>

                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; color: #64748b; font-size: 12px; text-transform: uppercase; margin-bottom: 5px;">📧 Email Address</div>
                    <p style="font-size: 16px; margin: 0; color: #0f172a; font-weight: 500;">{user.email}</p>
                </div>

                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="text-align: center; font-weight: 600; color: #dc2626; font-size: 18px; margin: 0;">
                    Please try to contact them right away.<br>If they do not respond, consider contacting local authorities.
                </p>
            </div>
            <div style="background-color: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                Sent automatically via Prana AI Safety System
            </div>
        </div>
    </body>
    </html>
    """

    notified_count = 0
    for contact in contacts:
        try:
            send_mail(
                subject,
                message_body,
                django_settings.DEFAULT_FROM_EMAIL if hasattr(django_settings, 'DEFAULT_FROM_EMAIL') else 'sos@pranaai.com',
                [contact.email],
                fail_silently=False,
                html_message=html_message
            )
            notified_count += 1
        except Exception as e:
            print(f"Error sending SOS email to {contact.email}: {str(e)}")
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
