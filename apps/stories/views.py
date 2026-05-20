from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Story
from .forms import StorySubmissionForm
from apps.accounts.decorators import alumni_only

@login_required(login_url='accounts:login')
def stories_list(request):
    stories = Story.objects.filter(status='approved').order_by('-published_at', '-submitted_at')
    paginator = Paginator(stories, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Keep the featured/small split pattern for UX
    stories_on_page = list(page_obj)
    featured_story = stories_on_page[0] if stories_on_page else None
    other_stories = stories_on_page[1:] if len(stories_on_page) > 1 else []

    context = {
        'featured_story': featured_story,
        'other_stories': other_stories,
        'page_obj': page_obj,
    }
    return render(request, 'stories/list.html', context)

@login_required(login_url='accounts:login')
def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id, status='approved')
    return render(request, 'stories/detail.html', {'story': story})

@alumni_only
def submit_story(request):
        
    if request.method == 'POST':
        form = StorySubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.status = 'pending_review'
            story.save()
            messages.success(request, 'Your story has been submitted for review. Thank you for inspiring!')
            return redirect('stories:stories_list')
    else:
        form = StorySubmissionForm()
        
    return render(request, 'stories/submit.html', {'form': form})

@alumni_only
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    # Security: check ownership
    if story.author != request.user:
        messages.error(request, "You are not authorized to delete this story.")
        return redirect('stories:story_detail', story_id=story_id)

    if request.method == "POST":
        story_title = story.title
        story.delete()
        messages.success(request, f"Story '{story_title}' has been deleted.")
        return redirect('stories:stories_list')

    return redirect('stories:story_detail', story_id=story_id)

@alumni_only
def edit_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    # Security: check ownership
    if story.author != request.user:
        messages.error(request, "You are not authorized to edit this story.")
        return redirect('stories:story_detail', story_id=story_id)

    if request.method == 'POST':
        form = StorySubmissionForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            updated_story = form.save(commit=False)
            updated_story.status = 'pending_review'  # Requires re-review after edit
            updated_story.save()
            messages.success(request, 'Your story has been updated and resubmitted for review.')
            return redirect('stories:stories_list')
    else:
        form = StorySubmissionForm(instance=story)

    return render(request, 'stories/edit_story.html', {'form': form, 'story': story})
