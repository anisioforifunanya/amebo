# Generated by Django 5.0.1 on 2024-03-02 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='likes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='events',
            name='category',
            field=models.CharField(choices=[('auto_boat_air', 'Auto, Boat & Air'), ('business_professional', 'Business & Professional'), ('charity_causes', 'Charity & Causes'), ('community_culture', 'Community & Culture'), ('family_education', 'Family & Education'), ('fashion_beauty', 'Fashion & Beauty'), ('film_media_ent', 'Film, Media & Entertainment'), ('food_drink', 'Food & Drink'), ('government_politics', 'Government & politics'), ('health_wellness', 'Health & Wellness'), ('hobbies_special_interest', 'Hobbies & Special Interest'), ('home_lifestyle', 'Home & Lifestyle'), ('music', 'Music'), ('other', 'Other'), ('performing_visual_arts', 'Performing & Visual Arts'), ('religion_spirituality', 'Religion & Spirituality'), ('school_activities', 'School Activities'), ('science_technology', 'Science & Technology'), ('seasonal_holiday', 'Seasonal & Holiday'), ('sports_fitness', 'Sports & Fitness'), ('travel_outdoor', 'Travel & Outdoor')], default='music', max_length=255, verbose_name='Event Category'),
        ),
        migrations.AlterField(
            model_name='events',
            name='event_type',
            field=models.CharField(choices=[('appearance_singing', 'Appearance or Singing'), ('attraction', 'Attraction'), ('camp_trip_retreat', 'Camp, Trip, or Retreat'), ('class_train_workshop', 'Class, Training, or Workshop'), ('concert_performance', 'Concert or Performance'), ('conference', 'Conference'), ('convention', 'Convention'), ('dinner_gala', 'Dinner or Gala'), ('festival_fair', 'Festival or Fair'), ('game_competition', 'Game or Competion'), ('meeting_network_event', 'Meeting or Network Event'), ('other', 'Other'), ('party_social_gathering', 'Party or Social Gathering'), ('race_endurance_event', 'Race or Endurance Event'), ('rally', 'Rally'), ('screening', 'Screening'), ('seminar_talk', 'Seminar or Talk'), ('tour', 'Tour'), ('tournament', 'Tournament'), ('trade_consumer_show', 'Trade Show, Consumer Show or Expo')], default='tour', max_length=255, verbose_name='Event Type'),
        ),
    ]
