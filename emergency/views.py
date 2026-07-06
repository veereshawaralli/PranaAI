import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.utils import timezone
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

    # Build map link using Google Maps
    if lat and lng:
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        location_text = f"Location: {address}\nGoogle Maps: {map_link}"
    else:
        map_link = ''
        location_text = "Location could not be determined."

    user = request.user
    user_name = user.get_full_name() or user.username

    subject = f"🚨 URGENT: SOS Help Needed from {user_name} 🚨"
    phone_display = user.phone_number or 'Not available'
    
    message_body = (
        f"*** 🚨 URGENT MEDICAL/SAFETY ALERT 🚨 ***\n\n"
        f"This is an automated emergency message from PranaAI.\n"
        f"{user_name} has activated their SOS panic button and urgently requires your assistance.\n\n"
        f"📍 Location Information:\n{location_text}\n\n"
        f"📞 Phone Number: {phone_display}\n"
        f"📧 Email Address: {user.email}\n\n"
        f"❗ ACTION REQUIRED: Please try to contact {user_name} right away. If they do not respond, consider contacting local emergency services or authorities immediately.\n\n"
        f"---\n"
        f"Sent automatically via PranaAI Safety System\n"
        f"Alert Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    map_html = f'<div style="margin-top: 15px;"><a href="{map_link}" style="display: inline-block; background: linear-gradient(135deg, #f59e0b, #d97706); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.2), 0 2px 4px -1px rgba(245, 158, 11, 0.1); letter-spacing: 0.5px;">📍 View Live Location on Map</a></div>' if map_link else ''
    
    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 40px 20px; -webkit-font-smoothing: antialiased;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); border: 1px solid #f3f4f6;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 25px 30px; text-align: center; border-bottom: 4px solid #b45309;">
                <h1 style="margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 1px; color: #ffffff; text-transform: uppercase; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">🚨 Emergency SOS Alert 🚨</h1>
            </div>
            
            <div style="padding: 35px 40px;">
                <!-- Urgent Notice Box -->
                <div style="background-color: #fffbeb; border: 1px solid #fcd34d; border-left: 5px solid #f59e0b; padding: 18px 20px; border-radius: 8px; margin-bottom: 30px;">
                    <p style="margin: 0; color: #b45309; font-weight: 600; font-size: 17px; line-height: 1.4;">
                        URGENT: <span style="font-weight: 700;">{user_name}</span> has activated their SOS panic button and requires immediate assistance!
                    </p>
                </div>
                <p style="font-size: 16px; line-height: 1.6; color: #4b5563; margin-top: 0; margin-bottom: 30px;">
                    You are receiving this automated message because you are registered as a primary emergency contact for <strong>{user_name}</strong> in the PranaAI app.
                </p>

                <!-- Location Details -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                    
                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;">Last Known Location</div>
                        <div style="font-size: 16px; color: #1e293b; font-weight: 500; line-height: 1.4;">{address}</div>
                        {map_html}
                    </div>

                    <div style="height: 1px; background-color: #e2e8f0; margin: 20px 0;"></div>

                    <div style="margin-bottom: 20px;">
                        <div style="font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;">Contact Phone Number</div>
                        <div style="font-size: 16px; color: #1e293b; font-weight: 500;">{phone_display}</div>
                    </div>

                    <div style="height: 1px; background-color: #e2e8f0; margin: 20px 0;"></div>

                    <div>
                        <div style="font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;">Email Address</div>
                        <div style="font-size: 16px; color: #1e293b; font-weight: 500;">{user.email}</div>
                    </div>
                    
                </div>

                <!-- Action Required -->
                <div style="text-align: center; margin-top: 35px; margin-bottom: 15px;">
                    <p style="font-weight: 600; color: #d97706; font-size: 18px; margin: 0 0 8px 0; line-height: 1.4;">
                        Please try to contact them right away.
                    </p>
                    <p style="color: #4b5563; font-size: 15px; margin: 0; line-height: 1.5;">
                        If they do not respond, consider contacting local emergency services or authorities immediately.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0; font-size: 13px; color: #64748b; font-weight: 500;">
                    Sent securely via PranaAI Safety System
                </p>
                <p style="margin: 6px 0 0 0; font-size: 12px; color: #94a3b8;">
                    Alert Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')} • Please do not reply.
                </p>
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
