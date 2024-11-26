import requests
from bs4 import BeautifulSoup
from .models import Institution, CareerField, Degree
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

def run_nirf_scraper():
    scraper = NIRFScraper()
    return scraper.update_institutions()


class NIRFScraper:
    def __init__(self):
        self.urls = {
            'Engineering': "https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html",
            'Management': "https://www.nirfindia.org/Rankings/2024/ManagementRanking.html",
            'Pharmacy': "https://www.nirfindia.org/Rankings/2024/PharmacyRanking.html",
            'Medical': "https://www.nirfindia.org/Rankings/2024/MedicalRanking.html",
            'Dental': "https://www.nirfindia.org/Rankings/2024/DentalRanking.html",
            'Law': "https://www.nirfindia.org/Rankings/2024/LawRanking.html",
            'Architecture': "https://www.nirfindia.org/Rankings/2024/ArchitectureRanking.html",
            'Agriculture': "https://www.nirfindia.org/Rankings/2024/AgricultureRanking.html"
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }


    def clean_name(self, text):
        """Clean institution name"""
        if not text or text.replace('.', '').isdigit():
            return None
        
        text = text.split('More Details')[0]
        text = text.replace('| |', '')
        text = text.replace('TLR (100)', '')
        text = text.replace('RPC (100)', '')
        text = text.replace('GO (100)', '')
        text = text.replace('OI (100)', '')
        text = text.replace('PERCEPTION (100)', '')
        
        text = ' '.join(text.split())
        return text.strip()

    def parse_numeric(self, text):
        """Parse numeric values"""
        try:
            value = ''.join(c for c in text if c.isdigit() or c == '.')
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    def extract_institution_data(self, row):
        """Extract institution data from a table row"""
        try:
            cells = row.find_all('td')
            
            if len(cells) < 4:  
                return None
            
            rank = self.parse_numeric(cells[0].text.strip())
            
            name = self.clean_name(cells[1].text)
            if not name:
                return None
                
            city = cells[2].text.strip() if len(cells) > 2 else ""
            state = cells[3].text.strip() if len(cells) > 3 else ""
            
            score = None
            for cell in reversed(cells):
                score = self.parse_numeric(cell.text)
                if score is not None:
                    break

            return {
                'name': name,
                'city': city,
                'state': state,
                'rank': int(rank) if rank else None,
                'score': score
            }
            
        except Exception as e:
            print(f"Error extracting data from row: {str(e)}")
            return None

    def scrape_institutions(self):
        """Scrape institutions from the NIRF website"""
        try:
            self.create_career_fields()
            self.create_default_degrees()
            
            for field_name, url in self.urls.items():
                print(f"\nScraping {field_name} institutions from {url}")
                
                try:
                    career_field = CareerField.objects.get(name=field_name)
                    response = requests.get(url, headers=self.headers, verify=False)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    tables = soup.find_all('table')
                    main_table = None
                    
                    for table in tables:
                        headers = table.find_all('th')
                        if headers and any('Institute' in th.text for th in headers):
                            main_table = table
                            break
                    
                    if not main_table:
                        print(f"No ranking table found for {field_name}")
                        continue
                    
                    rows = main_table.find_all('tr')[1:]  
                    processed_count = 0
                    
                    for row in rows:
                        try:
                            data = self.extract_institution_data(row)
                            if not data or not data['name']:
                                continue

                            with transaction.atomic():
                                institution, created = Institution.objects.update_or_create(
                                    name=data['name'],
                                    defaults={
                                        'location': f"{data['city']}, {data['state']}".strip(', '),
                                        'ranking': data['rank'],
                                        'nirf_score': data['score'],
                                        'nirf_ranking_year': 2024
                                    }
                                )

                                default_degrees = Degree.objects.filter(career_field=career_field)
                                institution.degrees.add(*default_degrees)

                                status = 'Created' if created else 'Updated'
                                print(f"{status}: {data['name']} (Rank: {data['rank']}, Score: {data['score']})")
                                processed_count += 1

                        except Exception as e:
                            print(f"Error processing row: {str(e)}")
                            continue
                            
                    print(f"\nProcessed {processed_count} institutions for {field_name}")

                except Exception as e:
                    print(f"Error scraping {field_name}: {str(e)}")
                    continue

            return True

        except Exception as e:
            print(f"Error in scrape_institutions: {str(e)}")
            return False

    def create_career_fields(self):
        """Create career fields"""
        fields = {
            'Engineering': 'Engineering encompasses the design, construction, and optimization of systems and solutions.'
        }
        
        for name, description in fields.items():
            CareerField.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'slug': name.lower()
                }
            )

    def create_default_degrees(self):
        """Create default degrees"""
        degrees = {
            'Engineering': [
                ('B.Tech', '4 years', 'Bachelor of Technology program'),
                ('M.Tech', '2 years', 'Master of Technology with specialization')
            ]
        }
        
        for field_name, degree_list in degrees.items():
            try:
                field = CareerField.objects.get(name=field_name)
                for name, duration, description in degree_list:
                    Degree.objects.get_or_create(
                        name=name,
                        career_field=field,
                        defaults={
                            'duration': duration,
                            'description': description,
                            'eligibility': 'Class 12 with PCM'
                        }
                    )
            except CareerField.DoesNotExist:
                print(f"Career field {field_name} not found")
        
    def update_institutions(self):
        """Main method to update all institution data"""
        return self.scrape_institutions()