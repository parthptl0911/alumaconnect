import os
import django
import sys
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
sys.path.append(r'c:\Users\Lenovo\Desktop\Aconnect')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almaconnect.settings')
django.setup()

from apps.mentorship.forms import MentorshipAcceptForm

def test_validation():
    print("Testing MentorshipAcceptForm validation...")
    
    # 1. Test past date
    past_date = timezone.now() - timedelta(days=1)
    form = MentorshipAcceptForm(data={
        'meeting_date': past_date,
        'platform': 'google_meet',
        'meeting_link': 'https://meet.google.com/abc-defg-hij'
    })
    
    if not form.is_valid():
        print(f"PASS: Past date rejected. Error: {form.errors.get('meeting_date')}")
    else:
        print("FAIL: Past date was accepted!")

    # 2. Test near future date (5 mins - should fail with 10 min buffer)
    near_future = timezone.now() + timedelta(minutes=5)
    form = MentorshipAcceptForm(data={
        'meeting_date': near_future,
        'platform': 'google_meet',
        'meeting_link': 'https://meet.google.com/abc-defg-hij'
    })
    
    if not form.is_valid():
        print(f"PASS: Near future date (5 mins) rejected. Error: {form.errors.get('meeting_date')}")
    else:
        print("FAIL: Near future date (5 mins) was accepted!")

    # 3. Test far future date (1 day - should pass)
    far_future = timezone.now() + timedelta(days=1)
    form = MentorshipAcceptForm(data={
        'meeting_date': far_future,
        'platform': 'google_meet',
        'meeting_link': 'https://meet.google.com/abc-defg-hij'
    })
    
    if form.is_valid():
        print("PASS: Far future date accepted.")
    else:
        print(f"FAIL: Far future date was rejected! Error: {form.errors}")

if __name__ == "__main__":
    test_validation()
