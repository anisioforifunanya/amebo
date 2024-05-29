from django.db import models
from users.models import AppUsers


class Store(models.Model):
    category_options = (
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home_kitchen', 'Home & Kitchen'),
        ('health_beauty', 'Health & Beauty'),
        ('toys_games', 'Toys & Games'),
        ('sports_outdoors', 'Sports & Outdoors'),
        ('books', 'Books'),
        ('automotive', 'Automotive'),
        ('grocery', 'Grocery'),
        ('pet_supplies', 'Pet Supplies'),
        ('tools', 'Tools & Home Imporovement'),
        ('baby', 'Baby'),
        ('handmade', 'Handmade'),
        ('software', 'Software'),
    )
    condition_options = (
        ('new', 'Brand New'),
        ('fairly_used', 'Fairly used')
    )
    posted_by = models.ForeignKey(AppUsers, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length= 500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(choices=category_options, max_length= 500, null=True, blank=True)
    condition = models.CharField(choices=condition_options, max_length= 500, null=True, blank=True)
    location = models.CharField(max_length= 500, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    picture_url = models.URLField(max_length= 500, null=True, blank=True)
    phone_no = models.CharField(max_length= 500, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.category}"

