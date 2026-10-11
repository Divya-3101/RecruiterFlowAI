from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from accounts.decorators import recruiter_required
from .models import Job
from .forms import JobForm


@login_required
@recruiter_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f"Job posting '{job.title}' published successfully!")
            return redirect('job_list')
    else:
        form = JobForm()
    return render(request, 'jobs/create_job.html', {'form': form})


@login_required
@recruiter_required
def update_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to edit this job posting.")
        return redirect('job_list')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job posting '{job.title}' updated successfully!")
            return redirect('job_list')
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/update_job.html', {'form': form, 'job': job})


@login_required
@recruiter_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter == request.user:
        title = job.title
        job.delete()
        messages.success(request, f"Job '{title}' deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this job.")
    return redirect('job_list')


def job_list(request):
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    min_salary = request.GET.get('min_salary', '').strip()

    jobs = Job.objects.all().order_by('-created_at')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(required_skills__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if min_salary:
        try:
            jobs = jobs.filter(salary__gte=int(min_salary))
        except ValueError:
            pass

    applied_job_ids = set()
    saved_job_ids = set()
    if request.user.is_authenticated and request.user.role == 'candidate':
        from applications.models import Application, SavedJob
        applied_job_ids = set(
            Application.objects.filter(candidate=request.user).values_list('job_id', flat=True)
        )
        saved_job_ids = set(
            SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
        )

    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'jobs/job_list.html',
        {
            'page_obj': page_obj,
            'query': query,
            'location': location,
            'min_salary': min_salary,
            'applied_job_ids': applied_job_ids,
            'saved_job_ids': saved_job_ids,
        }
    )