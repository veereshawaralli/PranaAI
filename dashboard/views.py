from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MedicineReminder
from .forms import MedicineReminderForm

@login_required
def dashboard_home(request):
    reminders = MedicineReminder.objects.filter(user=request.user).order_by('time')
    return render(request, 'dashboard/dashboard.html', {'reminders': reminders})

@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = MedicineReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Medicine reminder added successfully!')
            return redirect('dashboard_home')
    else:
        form = MedicineReminderForm()
    
    return render(request, 'dashboard/add_reminder.html', {'form': form})
