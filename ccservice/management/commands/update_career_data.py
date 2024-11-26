# Project/ccservice/management/commands/update_career_data.py
from django.core.management.base import BaseCommand
from ccservice.scrapers import CareerScraper  # Updated import path

class Command(BaseCommand):
    help = 'Update career data from external sources'

    def handle(self, *args, **options):
        scraper = CareerScraper()
        
        self.stdout.write('Starting data update...')
        
        try:
            scraper.scrape_shiksha()
            self.stdout.write('Completed Shiksha scraping')
            
            scraper.scrape_career360()
            self.stdout.write('Completed Career360 scraping')
            
            scraper.scrape_payscale()
            self.stdout.write('Completed PayScale scraping')
            
            scraper.scrape_institutions()
            self.stdout.write('Completed institutions scraping')
            
            self.stdout.write(self.style.SUCCESS('Successfully updated all data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating data: {str(e)}'))
