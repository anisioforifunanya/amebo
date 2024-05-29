from django.db import models

class Events(models.Model):
    event_type_options = (
        ('physical', 'Physical'),
        ('virtual', 'Virtual'),
        ('hybrid', 'Hybrid')
    )
    category_options = (
        ('auto_boat_air', 'Auto, Boat & Air'),
        ('business_professional', 'Business & Professional'),
        ('charity_causes', 'Charity & Causes'),
        ('community_culture', 'Community & Culture'),
        ('family_education', 'Family & Education'),
        ('fashion_beauty', 'Fashion & Beauty'),
        ('film_media_ent', 'Film, Media & Entertainment'),
        ('food_drink', 'Food & Drink'),
        ('government_politics', 'Government & politics'),
        ('health_wellness', 'Health & Wellness'),
        ('hobbies_special_interest', 'Hobbies & Special Interest'),
        ('home_lifestyle', 'Home & Lifestyle'),
        ('music', 'Music'),
        ('other', 'Other'),
        ('performing_visual_arts', 'Performing & Visual Arts'),
        ('religion_spirituality', 'Religion & Spirituality'),
        ('school_activities', 'School Activities'),
        ('science_technology', 'Science & Technology'),
        ('seasonal_holiday', 'Seasonal & Holiday'),
        ('sports_fitness', 'Sports & Fitness'),
        ('travel_outdoor', 'Travel & Outdoor')
    )
    created_by = models.ForeignKey('users.AppUsers', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    organizer = models.CharField(max_length=500, null=True, blank=True)
    event_type = models.CharField('Event Type', choices=event_type_options, max_length=255, default='physical')
    category = models.CharField('Event Category', choices=category_options, max_length=255, default='music')
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=1500, null=True, blank=True)
    virtual_url = models.URLField(max_length=500, null=True, blank=True)
    date = models.CharField(max_length=500, null=True, blank=True)
    time = models.CharField(max_length=500, null=True, blank=True)
    picture = models.URLField(max_length=1500, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    google_map_link = models.URLField(max_length=1500, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.organizer}"
