from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from apps.accounts.decorators import alumni_only
from .models import Event, RSVP

@alumni_only
def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('date', 'time')
    paginator = Paginator(events, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'events/list.html', {'page_obj': page_obj})

@alumni_only
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    user_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    return render(request, 'events/detail.html', {'event': event, 'user_rsvp': user_rsvp})

from django.db import transaction

@alumni_only
def event_rsvp(request, event_id):
    if request.method == 'POST':
        status = request.POST.get('status', 'attending')
        
        try:
            with transaction.atomic():
                # Lock the event row for the duration of the transaction to prevent race conditions
                event = Event.objects.select_for_update().get(id=event_id, is_active=True)
                
                if status == 'attending':
                    current_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
                    # Re-check capacity if user is not already attending
                    if event.is_full and (not current_rsvp or current_rsvp.status != 'attending'):
                        messages.error(request, "Sorry, this event has reached full capacity.")
                        return redirect('events:detail', event_id=event.id)
                
                RSVP.objects.update_or_create(
                    user=request.user,
                    event=event,
                    defaults={'status': status}
                )
                
                if status == 'attending':
                    messages.success(request, f"You have successfully RSVP'd for {event.title}.")
                else:
                    messages.success(request, f"Your RSVP for {event.title} has been updated to Not Attending.")
        except Exception as e:
            messages.error(request, "An error occurred during RSVP. Please try again.")
            
        return redirect('events:detail', event_id=event_id)
        
    return redirect('events:detail', event_id=event_id)
