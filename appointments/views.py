from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DoctorProfile, Appointment
from .forms import AppointmentForm

def doctor_list(request):
    doctors = DoctorProfile.objects.all()
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doctor
            appointment.save()
            name = doctor.user.get_full_name() or doctor.user.username
            messages.success(request, f"Your appointment with Dr. {name} has been requested successfully.")
            return redirect('appointments:my_appointments')
    else:
        form = AppointmentForm()
        
    return render(request, 'appointments/book.html', {'form': form, 'doctor': doctor})

@login_required
def my_appointments(request):
    if request.user.is_doctor:
        if not hasattr(request.user, 'doctor_profile'):
            messages.error(request, "Your doctor profile is not setup yet. Please contact admin.")
            return redirect('home')
        appointments = request.user.doctor_profile.doctor_appointments.all()
        is_patient = False
    else:
        appointments = request.user.patient_appointments.all()
        is_patient = True
        
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments,
        'is_patient': is_patient
    })

@login_required
def update_status(request, appointment_id, status):
    if not request.user.is_doctor:
        messages.error(request, "Permission denied. Only doctors can update statuses.")
        return redirect('appointments:my_appointments')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    if status in dict(Appointment.STATUS_CHOICES):
        appointment.status = status
        appointment.save()
        messages.success(request, f"Appointment status updated to {status}.")
        
    return redirect('appointments:my_appointments')
