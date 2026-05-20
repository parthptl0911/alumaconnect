
import django, os, sys
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almaconnect.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.jobs.models import Job, JobApplication
from apps.mentorship.models import MentorshipRequest
from apps.fundraising.models import Campaign, Donation
from apps.stories.models import Story
from apps.events.models import Event, RSVP
from django.test import Client

student = CustomUser.objects.get(email='student@college.edu')
alumni = CustomUser.objects.get(email='rahul.mehta@google.com')
c_s = Client()
c_s.force_login(student)
c_a = Client()
c_a.force_login(alumni)
c_u = Client()

urls = [
    '/accounts/',
    '/accounts/dashboard/',
    '/alumni/',
    '/jobs/',
    '/jobs/post/',
    '/fundraising/',
    '/fundraising/campaign/1/',
    '/stories/',
    '/stories/submit/',
    '/events/',
    '/mentorship/',
]

print('URL | unauth | student | alumni')
for u in urls:
    ru = c_u.get(u).status_code
    rs = c_s.get(u).status_code
    ra = c_a.get(u).status_code
    print('%s | %d | %d | %d' % (u, ru, rs, ra))

print()
print('=== BUSINESS LOGIC ===')
print('Active Jobs:', Job.objects.filter(is_active=True).count())
print('Total Applications:', JobApplication.objects.count())
print('Student apps:', JobApplication.objects.filter(applicant=student).count())

for j in Job.objects.all():
    apps = JobApplication.objects.filter(job=j).count()
    print('  Job: %s | apps: %d' % (j.title, apps))

print()
print('Mentorship requests:', MentorshipRequest.objects.count())
for m in MentorshipRequest.objects.all():
    print('  %s -> %s | %s' % (m.student.email, m.mentor.email, m.status))

print()
print('Campaigns:')
for c in Campaign.objects.all():
    print('  %s | raised=%s | target=%s | progress=%d%%' % (c.title, c.current_amount, c.target_amount, c.progress_percentage))

print()
print('Stories approved:', Story.objects.filter(status='approved').count())
print('Stories pending:', Story.objects.filter(status='pending_review').count())

print()
print('Events:')
for e in Event.objects.all():
    attending = RSVP.objects.filter(event=e, status='attending').count()
    print('  %s | capacity=%d | attending=%d | full=%s' % (e.title, e.capacity, attending, e.is_full))

print()
print('=== DUPLICATE PREVENTION ===')
dup_apps = {}
for app in JobApplication.objects.all():
    key = (app.applicant_id, app.job_id)
    dup_apps[key] = dup_apps.get(key, 0) + 1
dups = {k: v for k, v in dup_apps.items() if v > 1}
print('Duplicate job applications:', len(dups), '(0 = good)')

dup_mr = {}
for mr in MentorshipRequest.objects.filter(status='pending'):
    key = (mr.student_id, mr.mentor_id)
    dup_mr[key] = dup_mr.get(key, 0) + 1
dups_mr = {k: v for k, v in dup_mr.items() if v > 1}
print('Duplicate pending mentorship:', len(dups_mr), '(0 = good)')
