from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def alumni_only(view_func):
    @login_required(login_url='accounts:login')
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'alumni' or request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access Denied. Only alumni can access this feature.")
        return redirect('accounts:dashboard')
    return _wrapped_view

def student_only(view_func):
    @login_required(login_url='accounts:login')
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 'student' or request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access Denied. Only students can access this feature.")
        return redirect('accounts:dashboard')
    return _wrapped_view
