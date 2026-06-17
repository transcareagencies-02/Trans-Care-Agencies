from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE = (
        ('quote', 'Quote Required'),
        ('cart', 'Add to Cart'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE)
    fuel_savings_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payback_months = models.PositiveIntegerField(default=0)
    # 🧠 INVENTORY FIELDS
    stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)  # alert threshold
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    warranty_months = models.PositiveIntegerField(default=12)

    installation_required = models.BooleanField(default=True)

    delivery_time_days = models.PositiveIntegerField(default=7)

    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

    # 🔥 helper logic
    def is_low_stock(self):
        return self.stock <= self.reorder_level
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product.name} Image"
    
class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    name = models.CharField(max_length=100)   # e.g. Power Output
    value = models.CharField(max_length=255)  # e.g. 50 kW

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} Review"
    
class ProductDocument(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='products/documents/')

    def __str__(self):
        return self.title

class QuoteRequest(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    institution_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    quantity = models.IntegerField()

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='quotes/', blank=True, null=True)

    quotation_document = models.FileField(
        upload_to='quotes/quotation/',
        blank=True,
        null=True,
        help_text='Upload the quotation document for this customer.'
    )

    admin_note = models.TextField(
        blank=True,
        null=True,
        help_text='Optional response note for the customer.'
    )

    quoted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('quoted', 'Quoted'),
        ),
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institution_name} - {self.product.name}"