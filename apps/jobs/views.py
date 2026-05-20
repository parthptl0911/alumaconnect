from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from apps.accounts.decorators import student_only, alumni_only

@login_required(login_url='accounts:login')
def jobs_list(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(jobs, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'jobs/list.html', {'page_obj': page_obj})

@login_required(login_url='accounts:login')
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@alumni_only
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f"Job '{job.title}' posted successfully.")
            return redirect('jobs:jobs_list')
    else:
        form = JobForm()

    return render(request, 'jobs/post.html', {'form': form})

@alumni_only
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Security: check ownership
    if job.posted_by != request.user:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully.")
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required(login_url='accounts:login')
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # 1. Block owner from applying to their own job
    if job.posted_by == request.user:
        messages.error(request, "You cannot apply to your own job listing.")
        return redirect('jobs:job_detail', job_id=job_id)

    # 2. Check for existing application
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Send Notification Emails
            try:
                from django.core.mail import EmailMessage, send_mail
                from django.conf import settings
                
                # 1. To Recruiter (with Resume Attachment)
                email = EmailMessage(
                    subject='New Job Application Received',
                    body=f"A new candidate has applied for your job: {job.title}\n\n"
                         f"Name: {application.full_name}\n"
                         f"Email: {application.email}\n\n"
                         f"Message:\n{application.cover_letter}",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[job.posted_by.email],
                )
                
                if application.resume:
                    print("Sending email with attachment:", application.resume.path)
                    email.attach_file(application.resume.path)
                
                email.send()
                print("RECRUITER EMAIL SENT WITH ATTACHMENT")
                
                # 2. To Applicant (Confirmation)
                send_mail(
                    'Application Submitted Successfully',
                    f"Hello {application.full_name},\n\n"
                    f"You have successfully applied for the position of '{job.title}' at {job.company}.\n"
                    f"The recruiter will review your application and contact you if they're interested.\n\n"
                    "Good luck!",
                    settings.EMAIL_HOST_USER,
                    [application.email],
                    fail_silently=False,
                )
                print("APPLICANT EMAIL SENT")
            except Exception as e:
                print("JOB EMAIL ERROR:", e)
                
            messages.success(request, f"Application for '{job.title}' submitted successfully.")
            return redirect('accounts:dashboard')
    else:
        form = JobApplicationForm(initial={
            'full_name': request.user.full_name,
            'email': request.user.email
        })

    return render(request, 'jobs/apply.html', {'form': form, 'job': job})

@alumni_only
def manage_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.applications.all().order_by('-applied_at')
    return render(request, 'jobs/applicants.html', {
        'job': job,
        'applications': applications
    })

@alumni_only
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status for {application.applicant.email} updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
            
    return redirect('jobs:manage_applicants', job_id=application.job.id)

@login_required(login_url='accounts:login')
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Security: check ownership
    if job.posted_by != request.user:
        messages.error(request, "You are not authorized to delete this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == "POST":
        job.delete()
        messages.success(request, f"Job '{job.title}' has been deleted.")
        return redirect('jobs:jobs_list')

    return redirect('jobs:job_detail', job_id=job_id)
