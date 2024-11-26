# ccservice/management/commands/initialize_career_data.py
from django.core.management.base import BaseCommand
from ccservice.scrapers import NIRFScraper, initialize_career_data

class Command(BaseCommand):
    help = 'Initialize career data and scrape NIRF rankings'

    def handle(self, *args, **options):
        self.stdout.write('Initializing career data...')
        initialize_career_data()
        
        self.stdout.write('Scraping NIRF rankings...')
        scraper = NIRFScraper()
        scraper.update_institutions()
        
        self.stdout.write(self.style.SUCCESS('Successfully initialized career data and updated NIRF rankings'))