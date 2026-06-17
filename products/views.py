from django.shortcuts import get_object_or_404, render

# Create your views here.
from .models import Product

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    return render(request, 'products.html', {'products': products})

def product_detail(request, id):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            'images',
            'specs',
            'reviews',
            'documents'
        ),
        id=id
    )

    viewed_ids = [item for item in request.session.get('recently_viewed', []) if item != id]
    viewed_ids.insert(0, id)
    viewed_ids = viewed_ids[:6]
    request.session['recently_viewed'] = viewed_ids
    request.session.modified = True

    recently_viewed_products = list(
        Product.objects.filter(id__in=viewed_ids, is_active=True).exclude(id=product.id)
    )
    recently_viewed_products.sort(key=lambda item: viewed_ids.index(item.id))

    reviews = list(product.reviews.all().order_by('-created_at'))
    review_count = len(reviews)
    average_rating = (
        round(sum(review.rating for review in reviews) / review_count, 1)
        if review_count
        else 0.0
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    return render(request, "products/detail.html", {
        "product": product,
        "related_products": related_products,
        "recently_viewed_products": recently_viewed_products[:4],
        "reviews": reviews[:6],
        "review_summary": {
            "average_rating": average_rating,
            "count": review_count,
        },
    })