"""
Root URL configuration for AlumaConnect.
Each app has its own urls.py included here.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from django.core.mail import send_mail
from django.http import HttpResponse

def test_email(request):
    try:
        send_mail(
            'Test Email',
            'SMTP is working successfully.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print("EMAIL SENT SUCCESS")
        return HttpResponse("Email Sent Successfully")
    except Exception as e:
        print("EMAIL ERROR:", e)
        return HttpResponse(f"Error: {e}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-email/', test_email),

    # Root redirect → accounts home
    path('', RedirectView.as_view(url='/accounts/', permanent=False), name='home'),

    # App URL namespaces
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('alumni/', include('apps.alumni.urls', namespace='alumni')),
    path('mentorship/', include('apps.mentorship.urls', namespace='mentorship')),
    path('jobs/', include('apps.jobs.urls', namespace='jobs')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('fundraising/', include('apps.fundraising.urls', namespace='fundraising')),
    path('stories/', include('apps.stories.urls', namespace='stories')),
    path('chat/', include('apps.chat.urls', namespace='chat')),
]

# Serve media/static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
