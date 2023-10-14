# Generated by Django 3.2.9 on 2022-01-24 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0033_sectiondata_section_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectiondata',
            name='title',
            field=models.CharField(choices=[('why_to_use', 'Why to use'), ('demo_videos', 'Demo Videos'), ('business_opportunity', 'Business Opportunity'), ('training_videos', 'Training Videos'), ('motivational_videos', 'Motivational Videos'), ('success_stories', 'Success Stories'), ('testimonial_videos', 'Testimonial Videos'), ('about_modicare', 'About Modicare'), ('become_a_partner', 'Become a Partner'), ('previous_events', 'Previous Events'), ('upcoming_events', 'Upcoming Events'), ('book_ticket', 'Book Ticket')], max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='videosections',
            name='section',
            field=models.CharField(choices=[('why_to_use', 'Why to use'), ('demo_videos', 'Demo Videos'), ('business_opportunity', 'Business Opportunity'), ('training_videos', 'Training Videos'), ('motivational_videos', 'Motivational Videos'), ('success_stories', 'Success Stories'), ('testimonial_videos', 'Testimonial Videos')], default=None, max_length=200, null=True, unique=True),
        ),
    ]
