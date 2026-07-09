from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from apps.reviews.models import Review

@staff_member_required(login_url='admin_login')
def review_list(request):
    reviews = Review.objects.all().select_related('user', 'product')
    return render(request, 'admin/reviews/review_list.html', {'reviews': reviews})

@staff_member_required(login_url='admin_login')
def toggle_review_status(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_active = not review.is_active
    review.save()
    status = "activated" if review.is_active else "deactivated"
    messages.success(request, f'Review {status} successfully.')
    return redirect('review_list')
