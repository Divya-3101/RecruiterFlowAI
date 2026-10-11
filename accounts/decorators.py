from django.shortcuts import redirect
from functools import wraps


def recruiter_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'recruiter':
            return redirect('job_list')
        return view_func(
            request,
            *args,
            **kwargs
        )
    return wrapper


def candidate_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'candidate':
            return redirect('job_list')
        return view_func(
            request,
            *args,
            **kwargs
        )
    return wrapper