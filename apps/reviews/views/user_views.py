from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from apps.reviews.models import Review
from apps.orders.models import OrderItem

@login_required(login_url='login')
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating', 5)
        review_title = request.POST.get('review_title', '').strip()
        review_text = request.POST.get('review_text', '').strip()

        if not review_text:
            messages.error(request, 'Review text cannot be empty.')
            return redirect('product_detail', product_id=product.id)

        # Check if user actually purchased the product and it is delivered
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product_variant__product=product,
            order__order_status='delivered'
        ).exists()

        if not has_purchased:
            messages.error(request, 'You can only review products that you have purchased and received.')
            return redirect('product_detail', product_id=product.id)

        review, created = Review.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={
                'rating': rating,
                'review_title': review_title,
                'review_text': review_text,
                'is_verified_purchase': has_purchased
            }
        )

        messages.success(request, 'Your review has been submitted successfully!')
        return redirect('product_detail', product_id=product.id)
    return redirect('shop')