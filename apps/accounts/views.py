from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import CustomUser, WhitelistEmail, StudentProfile, AlumniProfile
from .forms import LoginForm, RegistrationForm, StudentProfileForm, AlumniProfileForm
from apps.mentorship.models import MentorshipRequest

def home(request):
    """Landing page — renders home.html which contains the full prototype UI."""
    return render(request, 'home.html')

@login_required(login_url='accounts:login')
def dashboard(request):
    from apps.jobs.models import Job, JobApplication
    from apps.events.models import RSVP
    from apps.stories.models import Story
    
    context = {}
    context['user_stories'] = Story.objects.filter(author=request.user).order_by('-submitted_at')
    
    if request.user.role == 'student':
        # Data for students
        sent_mentorship_requests = MentorshipRequest.objects.filter(student=request.user).order_by('-created_at')
        job_applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
        
        context.update({
            'mentorship_requests': sent_mentorship_requests,
            'job_applications': job_applications,
            'total_requests': sent_mentorship_requests.count(),
            'total_jobs': job_applications.count(),
            'stats': {
                'mentorship_requests': sent_mentorship_requests.count(),
                'applied_jobs': job_applications.count(),
            },
            'suggested_alumni': AlumniProfile.objects.all()[:3]
        })
        
    elif request.user.role == 'alumni':
        # Data for alumni
        received_mentorship_requests = MentorshipRequest.objects.filter(mentor=request.user, status='pending').order_by('-created_at')
        all_mentorship_requests = MentorshipRequest.objects.filter(mentor=request.user).order_by('-created_at')
        posted_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
        received_job_apps = JobApplication.objects.filter(job__posted_by=request.user).order_by('-applied_at')
        event_rsvps = RSVP.objects.filter(user=request.user, status='attending')
        
        context.update({
            'mentorship_requests': received_mentorship_requests,
            'all_mentorship_requests': all_mentorship_requests,
            'posted_jobs': posted_jobs,
            'job_applications': received_job_apps,
            'total_requests': all_mentorship_requests.count(),
            'total_jobs': posted_jobs.count(),
            'stats': {
                'pending_requests': received_mentorship_requests.count(),
                'jobs_posted': posted_jobs.count(),
                'event_participation': event_rsvps.count()
            }
        })
        
    elif request.user.role == 'admin':
        context['stats'] = {
            'total_users': CustomUser.objects.count(),
            'pending_approvals': 0
        }

    # Conversations preview – shared across all roles for the Messages panel
    from apps.chat.models import Conversation
    from django.db.models import Max
    conversations = request.user.conversations.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time', '-created_at')[:5]

    conversations_data = []
    for convo in conversations:
        other_user = convo.get_other_user(request.user)
        last_message = convo.get_last_message()
        conversations_data.append({
            'conversation': convo,
            'other_user': other_user,
            'last_message': last_message,
        })
    context['conversations_data'] = conversations_data

    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='accounts:login')
def profile_view(request):
    from apps.stories.models import Story
    from apps.jobs.models import Job
    profile_user = request.user
    source = request.GET.get('from', '')
    context = {'profile_user': profile_user, 'source': source}

    if profile_user.role == 'student':
        context['profile'] = getattr(profile_user, 'student_profile', None)
    elif profile_user.role == 'alumni':
        context['profile'] = getattr(profile_user, 'alumni_profile', None)

    profile = context.get('profile')
    context['skills_list'] = [s.strip() for s in profile.skills.split(',')] if profile and profile.skills else []

    context['stories'] = Story.objects.filter(
        author=profile_user, status='approved'
    ).order_by('-submitted_at')
    context['jobs'] = Job.objects.filter(
        posted_by=profile_user
    ).order_by('-created_at') if profile_user.role == 'alumni' else []

    return render(request, 'accounts/profile_view.html', context)

@login_required(login_url='accounts:login')
def public_profile_view(request, user_id):
    from apps.stories.models import Story
    from apps.jobs.models import Job
    target_user = get_object_or_404(CustomUser, id=user_id)
    source = request.GET.get('from', '')
    context = {'profile_user': target_user, 'source': source}

    if target_user.role == 'student':
        context['profile'] = getattr(target_user, 'student_profile', None)
    elif target_user.role == 'alumni':
        context['profile'] = getattr(target_user, 'alumni_profile', None)

    profile = context.get('profile')
    context['skills_list'] = [s.strip() for s in profile.skills.split(',')] if profile and profile.skills else []

    context['stories'] = Story.objects.filter(
        author=target_user, status='approved'
    ).order_by('-submitted_at')
    context['jobs'] = Job.objects.filter(
        posted_by=target_user
    ).order_by('-created_at') if target_user.role == 'alumni' else []

    return render(request, 'accounts/profile_view.html', context)

@login_required(login_url='accounts:login')
@login_required(login_url='accounts:login')
def profile_edit(request):
    if request.user.role == 'student':
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        form_class = StudentProfileForm
    elif request.user.role == 'alumni':
        profile, created = AlumniProfile.objects.get_or_create(user=request.user)
        form_class = AlumniProfileForm
    else:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile_view')
    else:
        form = form_class(instance=profile)
        
    return render(request, 'accounts/profile_edit.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    step = 1
    context = {'step': step}

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'check_email':
            email = request.POST.get('email', '').strip().lower()
            try:
                whitelist_entry = WhitelistEmail.objects.get(email=email)
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'Account already exists. Please login.')
                else:
                    context['step'] = 2
                    context['email'] = email
                    context['whitelist'] = whitelist_entry
                    context['form'] = RegistrationForm(initial={'email': email})
            except WhitelistEmail.DoesNotExist:
                messages.error(request, 'Email not authorized. You must be on the college whitelist to register.')
                context['email'] = email

        elif action == 'register':
            form = RegistrationForm(request.POST)
            email = request.POST.get('email', '').strip().lower()
            
            if form.is_valid():
                whitelist_entry = WhitelistEmail.objects.get(email=email)
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=form.cleaned_data['password'],
                        role=whitelist_entry.role,
                        first_name=whitelist_entry.first_name,
                        last_name=whitelist_entry.last_name,
                    )
                    # Profile is now handled by post_save signal in signals.py
                    login(request, user)
                    return redirect('accounts:dashboard')
            else:
                try:
                    whitelist_entry = WhitelistEmail.objects.get(email=email)
                    context['step'] = 2
                    context['email'] = email
                    context['whitelist'] = whitelist_entry
                    context['form'] = form
                except WhitelistEmail.DoesNotExist:
                    messages.error(request, 'Email not authorized.')
                
    return render(request, 'accounts/register.html', context)

def logout_view(request):
    logout(request)
    return redirect('accounts:index')
