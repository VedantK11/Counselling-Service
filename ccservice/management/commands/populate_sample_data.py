# ccservice/management/commands/populate_sample_data.py

from django.core.management.base import BaseCommand
from ccservice.models import Institution, CareerField, Degree

class Command(BaseCommand):
    help = 'Populate sample institution data'

    def handle(self, *args, **options):
        # Create Engineering field
        engineering_field, _ = CareerField.objects.get_or_create(
            name="Engineering",
            defaults={
                'description': 'Engineering encompasses the design, construction, and optimization of systems and solutions.',
                'slug': 'engineering'
            }
        )

        # Create B.Tech degree
        btech_degree, _ = Degree.objects.get_or_create(
            name="B.Tech",
            career_field=engineering_field,
            defaults={
                'duration': '4 years',
                'description': 'Bachelor of Technology program',
                'eligibility': 'Class 12 PCM with minimum 60% marks'
            }
        )

        # Sample institutions
        institutions_data = [
            {
                'name': 'Indian Institute of Technology Madras',
                'location': 'Chennai, Tamil Nadu',
                'ranking': 1,
                'nirf_score': 90.04,
                'teaching_score': 89.42,
                'research_score': 91.36,
                'placement_score': 88.75
            },
            {
                'name': 'Indian Institute of Technology Delhi',
                'location': 'New Delhi, Delhi',
                'ranking': 2,
                'nirf_score': 88.96,
                'teaching_score': 87.89,
                'research_score': 90.12,
                'placement_score': 87.44
            },
            # Add more institutions as needed
        ]

        for data in institutions_data:
            institution, created = Institution.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            institution.degrees.add(btech_degree)
            if created:
                self.stdout.write(f'Created institution: {institution.name}')
            else:
                self.stdout.write(f'Updated institution: {institution.name}')