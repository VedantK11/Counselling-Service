from django.core.management.base import BaseCommand
from ccservice.scrapers import NIRFScraper

class Command(BaseCommand):
    help = 'Scrape NIRF rankings data'

    def handle(self, *args, **options):
        self.stdout.write('Starting NIRF scraping...')
        
        scraper = NIRFScraper()
        success = scraper.update_institutions()
        
        if success:
            self.stdout.write(self.style.SUCCESS('Successfully scraped NIRF data'))
        else:
            self.stdout.write(self.style.ERROR('Failed to scrape NIRF data'))