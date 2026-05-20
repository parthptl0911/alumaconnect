from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MentorshipRequest, Mentorship
from .forms import MentorshipRequestForm, MentorshipAcceptForm, MentorshipRejectForm
from apps.accounts.models import CustomUser
from apps.accounts.decorators import student_only, alumni_only
from apps.chat.models import Conversation, Message

@student_only
def send_request(request, mentor_id):

    mentor = get_object_or_404(CustomUser, id=mentor_id, role='alumni')
    
    # Check for existing pending request
    if MentorshipRequest.objects.filter(student=request.user, mentor=mentor, status='pending').exists():
        messages.warning(request, "You already have a pending mentorship request with this mentor.")
        return redirect('mentorship:index')

    if request.method == 'POST':
        form = MentorshipRequestForm(request.POST)
        if form.is_valid():
            mentorship_request = form.save(commit=False)
            mentorship_request.student = request.user
            mentorship_request.mentor = mentor
            mentorship_request.save()
            messages.success(request, f"Mentorship request sent to {mentor.email} successfully.")
            return redirect('mentorship:index')
    else:
        form = MentorshipRequestForm()

    return render(request, 'mentorship/request.html', {'form': form, 'mentor': mentor})

@alumni_only
def accept_request(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user, status='pending')
    
    if request.method == 'POST':
        form = MentorshipAcceptForm(request.POST)
        if form.is_valid():
            # 1. Update Request
            mentorship_request.status = 'accepted'
            mentorship_request.save()
            
            # 2. Create Mentorship Record
            mentorship = form.save(commit=False)
            mentorship.request = mentorship_request
            mentorship.save()
            
            # 3. Chat Integration
            # Get or create conversation between mentor and student
            conversations = Conversation.objects.filter(participants=request.user).filter(participants=mentorship_request.student)
            if conversations.exists():
                conversation = conversations.first()
            else:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, mentorship_request.student)
            
            # Create the automated message
            content = f"""Mentorship Accepted 🎉

Meeting Details:
Date: {mentorship.meeting_date}
Platform: {mentorship.get_platform_display()}
Link: {mentorship.meeting_link}"""
            
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            messages.success(request, f"Mentorship from {mentorship_request.student.email} accepted and details shared.")
            return redirect('mentorship:index')
    
    return redirect('mentorship:index')

@alumni_only
def reject_request(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user, status='pending')
    
    if request.method == 'POST':
        form = MentorshipRejectForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            
            # 1. Update Request
            mentorship_request.status = 'rejected'
            mentorship_request.save()
            
            # 2. Chat Integration
            conversations = Conversation.objects.filter(participants=request.user).filter(participants=mentorship_request.student)
            if conversations.exists():
                conversation = conversations.first()
            else:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, mentorship_request.student)
            
            content = f"""Mentorship Request Rejected ❌

Reason:
{reason}"""
            
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            messages.success(request, f"Request from {mentorship_request.student.email} declined.")
            return redirect('mentorship:index')
            
    return redirect('mentorship:index')

@login_required(login_url='accounts:login')
def index(request):
    from apps.accounts.models import AlumniProfile
    context = {}

    if request.user.role == 'student':
        # Fetch all alumni users who have opted-in for mentorship
        alumni_users = CustomUser.objects.filter(
            role='alumni', 
            alumni_profile__is_mentor_available=True
        ).select_related('alumni_profile')
        
        # Get IDs of mentors the student already has a PENDING request with
        pending_mentor_ids = set(
            MentorshipRequest.objects.filter(
                student=request.user, status='pending'
            ).values_list('mentor_id', flat=True)
        )
        
        sent_requests = MentorshipRequest.objects.filter(
            student=request.user
        ).select_related('mentor').order_by('-created_at')
        
        context.update({
            'alumni_users': alumni_users,
            'pending_mentor_ids': pending_mentor_ids,
            'sent_requests': sent_requests,
        })

    elif request.user.role == 'alumni':
        received_requests = MentorshipRequest.objects.filter(
            mentor=request.user
        ).select_related('student').order_by('-created_at')
        
        context['received_requests'] = received_requests
        context['accept_form'] = MentorshipAcceptForm()
        context['reject_form'] = MentorshipRejectForm()

    return render(request, 'mentorship/index.html', context)

@login_required(login_url='accounts:login')
def delete_mentorship(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, id=request_id)

    # Security: check ownership (only the student who sent it can delete it)
    if mentorship_request.student != request.user:
        messages.error(request, "You are not authorized to withdraw this request.")
        return redirect('mentorship:index')

    if request.method == "POST":
        mentorship_request.delete()
        messages.success(request, "Mentorship request withdrawn successfully.")
        return redirect('mentorship:index')

    return redirect('mentorship:index')
