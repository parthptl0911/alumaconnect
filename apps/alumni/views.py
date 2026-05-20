from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from apps.accounts.models import CustomUser

@login_required(login_url='accounts:login')
def alumni_list(request):
    query = request.GET.get('q', '').strip()
    batch_filter = request.GET.get('batch', '').strip()
    role_filter = request.GET.get('role', '').strip()
    mentors_only = request.GET.get('mentors_only', '') == 'true'

    users = CustomUser.objects.exclude(role='admin') \
        .select_related('alumni_profile', 'student_profile') \
        .order_by('role', 'email')
    
    if mentors_only:
        users = users.filter(role='alumni', alumni_profile__is_mentor_available=True)

    if query:
        users = users.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(alumni_profile__company__icontains=query) |
            Q(alumni_profile__skills__icontains=query) |
            Q(alumni_profile__designation__icontains=query) |
            Q(alumni_profile__location__icontains=query) |
            Q(student_profile__skills__icontains=query)
        )

    if role_filter in ('alumni', 'student'):
        users = users.filter(role=role_filter)

    if batch_filter and batch_filter != 'All Batches':
        safe_batch = batch_filter.replace("Batch ", "").replace("'", "").strip()
        users = users.filter(alumni_profile__graduation_year__icontains=safe_batch)

    users = users.distinct()

    paginator = Paginator(users, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'alumni_list': page_obj,
        'query': query,
        'batch_filter': batch_filter,
        'role_filter': role_filter,
        'mentors_only': mentors_only,
    }
    return render(request, 'alumni/list.html', context)
