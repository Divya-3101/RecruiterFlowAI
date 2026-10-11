from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import recruiter_required

from jobs.models import Job
from .models import Application, SavedJob
from .forms import ApplicationForm, ApplicationStatusForm
from .matching_service import evaluate_application


@login_required
def apply_job(request, job_id):
    if request.user.role != 'candidate':
        messages.warning(request, "Only registered candidates can apply for jobs.")
        return redirect('job_list')

    job = get_object_or_404(Job, id=job_id)

    if Application.objects.filter(candidate=request.user, job=job).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('job_list')

    if job.recruiter == request.user:
        messages.warning(request, "You cannot apply to your own job.")
        return redirect('job_list')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            application.save()

            # Execute hybrid AI semantic & ATS skill matching
            evaluate_application(application)

            messages.success(
                request,
                f"Your application for '{job.title}' at {job.company} has been submitted!"
            )
            return redirect('my_applications')
    else:
        form = ApplicationForm()

    return render(
        request,
        'applications/apply_job.html',
        {
            'form': form,
            'job': job
        }
    )


@login_required
@recruiter_required
def recruiter_applications(request):
    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        'candidate',
        'job'
    ).order_by(
        '-final_score',
        '-applied_at'
    )

    for application in applications:
        application.matched_skills_list = [
            skill.strip()
            for skill in (application.matched_skills or '').split(',')
            if skill.strip()
        ]

        application.missing_skills_list = [
            skill.strip()
            for skill in (application.missing_skills or '').split(',')
            if skill.strip()
        ]

        score = application.final_score or 0

        if score >= 80:
            application.match_category = "Excellent Match"
        elif score >= 60:
            application.match_category = "Good Match"
        elif score >= 40:
            application.match_category = "Moderate Match"
        else:
            application.match_category = "Low Match"

    return render(
        request,
        'applications/recruiter_applications.html',
        {
            'applications': applications
        }
    )


@login_required
@recruiter_required
def recalculate_ai_match(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    result = evaluate_application(application)
    if result:
        messages.success(
            request,
            f"AI match recalculation complete for {application.candidate.username} (Score: {application.final_score}%)."
        )
    else:
        messages.warning(
            request,
            f"Recalculation finished with default scores for {application.candidate.username}."
        )

    return redirect('recruiter_applications')


@login_required
@recruiter_required
def application_detail(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related('candidate', 'job'),
        id=application_id,
        job__recruiter=request.user
    )

    matched_skills = [
        skill.strip()
        for skill in (application.matched_skills or '').split(',')
        if skill.strip()
    ]

    missing_skills = [
        skill.strip()
        for skill in (application.missing_skills or '').split(',')
        if skill.strip()
    ]

    context = {
        'application': application,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
    }

    return render(
        request,
        'applications/application_detail.html',
        context
    )


@login_required
@recruiter_required
def dashboard(request):
    total_jobs = Job.objects.filter(recruiter=request.user).count()
    total_applications = Application.objects.filter(job__recruiter=request.user).count()
    unique_candidates = Application.objects.filter(job__recruiter=request.user).values('candidate').distinct().count()
    recent_applications = Application.objects.filter(job__recruiter=request.user).select_related('candidate', 'job').order_by('-applied_at')[:5]

    context = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'unique_candidates': unique_candidates,
        'recent_applications': recent_applications,
    }
    return render(request, 'applications/dashboard.html', context)


@login_required
@recruiter_required
def update_application_status(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    if request.method == 'POST':
        form = ApplicationStatusForm(
            request.POST,
            instance=application
        )
        if form.is_valid():
            app = form.save()
            messages.success(
                request,
                f"Status updated to '{app.get_status_display()}' for {app.candidate.username}."
            )
            return redirect('recruiter_applications')
    else:
        form = ApplicationStatusForm(instance=application)

    return render(
        request,
        'applications/update_status.html',
        {
            'form': form,
            'application': application
        }
    )


@login_required
def my_applications(request):
    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-applied_at')

    return render(
        request,
        'applications/my_applications.html',
        {
            'applications': applications
        }
    )


@login_required
def save_job(request, job_id):
    if request.user.role != 'candidate':
        messages.warning(request, "Only candidates can bookmark jobs.")
        return redirect('job_list')

    job = get_object_or_404(Job, id=job_id)
    saved_job = SavedJob.objects.filter(user=request.user, job=job).first()

    if saved_job:
        saved_job.delete()
        messages.info(request, f"Removed '{job.title}' from your saved jobs.")
    else:
        SavedJob.objects.create(user=request.user, job=job)
        messages.success(request, f"Saved '{job.title}' to your bookmarks.")

    return redirect('job_list')


@login_required
def my_saved_jobs(request):
    if request.user.role != 'candidate':
        return redirect('home')

    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job').order_by('-saved_at')

    return render(
        request,
        'applications/my_saved_jobs.html',
        {'saved_jobs': saved_jobs}
    )


@login_required
def candidate_dashboard(request):
    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job')

    total_applications = applications.count()
    shortlisted = applications.filter(status='shortlisted').count()
    interviews = applications.filter(status='interview').count()
    saved_jobs = SavedJob.objects.filter(user=request.user).count()
    recent_applications = applications.order_by('-applied_at')[:5]

    return render(
        request,
        'applications/candidate_dashboard.html',
        {
            'total_applications': total_applications,
            'shortlisted': shortlisted,
            'interviews': interviews,
            'saved_jobs': saved_jobs,
            'recent_applications': recent_applications,
        }
    )