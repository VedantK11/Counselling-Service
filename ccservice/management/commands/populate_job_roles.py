# ccservice/management/commands/populate_job_roles.py
from django.core.management.base import BaseCommand
from ccservice.models import CareerField, JobRole

class Command(BaseCommand):
    help = 'Populate sample job roles for all career fields'

    def handle(self, *args, **options):
        career_roles = {
            'Engineering': [
                {
                    'title': 'Software Engineer',
                    'description': 'Develops software applications and systems using various programming languages and technologies',
                    'average_salary': '₹6-20 LPA',
                    'required_skills': 'Programming Languages (Python, Java, etc.), Data Structures, Algorithms, Problem-Solving'
                },
                {
                    'title': 'Systems Architect',
                    'description': 'Designs and oversees complex system architecture, ensuring scalability and efficiency',
                    'average_salary': '₹15-35 LPA',
                    'required_skills': 'System Design, Cloud Computing, Technical Leadership, Enterprise Architecture'
                },
                {
                    'title': 'Machine Learning Engineer',
                    'description': 'Develops AI and machine learning models for various applications',
                    'average_salary': '₹8-25 LPA',
                    'required_skills': 'Machine Learning, Python, Deep Learning, Data Analysis'
                }
            ],
            
            'Medical': [
                {
                    'title': 'General Physician',
                    'description': 'Provides primary healthcare services and manages various medical conditions',
                    'average_salary': '₹8-25 LPA',
                    'required_skills': 'Clinical Skills, Patient Care, Diagnostic Abilities, Medical Knowledge'
                },
                {
                    'title': 'Surgeon',
                    'description': 'Performs surgical procedures and provides pre/post-operative care',
                    'average_salary': '₹15-50 LPA',
                    'required_skills': 'Surgical Skills, Operating Room Experience, Critical Care, Emergency Medicine'
                },
                {
                    'title': 'Medical Researcher',
                    'description': 'Conducts medical research to advance healthcare knowledge and treatments',
                    'average_salary': '₹10-30 LPA',
                    'required_skills': 'Research Methodology, Data Analysis, Clinical Knowledge, Scientific Writing'
                }
            ],

            'Agriculture': [
                {
                    'title': 'Agricultural Scientist',
                    'description': 'Conducts research on crops, soil health, and farming techniques',
                    'average_salary': '₹5-15 LPA',
                    'required_skills': 'Research Methods, Crop Science, Soil Analysis, Agricultural Technology'
                },
                {
                    'title': 'Farm Manager',
                    'description': 'Manages farm operations and supervises agricultural production',
                    'average_salary': '₹4-12 LPA',
                    'required_skills': 'Farm Operations, Resource Management, Leadership, Agricultural Knowledge'
                },
                {
                    'title': 'Agribusiness Consultant',
                    'description': 'Provides consulting services for agricultural businesses and projects',
                    'average_salary': '₹6-18 LPA',
                    'required_skills': 'Business Analysis, Agricultural Knowledge, Consulting, Project Management'
                }
            ],

            'Architecture': [
                {
                    'title': 'Architect',
                    'description': 'Designs buildings and spaces while considering aesthetic and functional aspects',
                    'average_salary': '₹5-20 LPA',
                    'required_skills': 'AutoCAD, Design Skills, Project Management, 3D Modeling'
                },
                {
                    'title': 'Urban Planner',
                    'description': 'Plans and designs urban spaces and communities',
                    'average_salary': '₹6-18 LPA',
                    'required_skills': 'Urban Planning, GIS, Policy Analysis, Sustainable Development'
                },
                {
                    'title': 'Interior Architect',
                    'description': 'Specializes in designing interior spaces and layouts',
                    'average_salary': '₹4-15 LPA',
                    'required_skills': 'Interior Design, Space Planning, 3D Visualization, Material Knowledge'
                }
            ],

            'Law': [
                {
                    'title': 'Corporate Lawyer',
                    'description': 'Handles legal matters for businesses and corporations',
                    'average_salary': '₹8-30 LPA',
                    'required_skills': 'Corporate Law, Contract Drafting, Negotiation, Business Understanding'
                },
                {
                    'title': 'Litigation Lawyer',
                    'description': 'Represents clients in court proceedings and legal disputes',
                    'average_salary': '₹5-25 LPA',
                    'required_skills': 'Court Procedures, Legal Research, Advocacy, Client Management'
                },
                {
                    'title': 'Legal Consultant',
                    'description': 'Provides legal consultation and advisory services',
                    'average_salary': '₹7-20 LPA',
                    'required_skills': 'Legal Analysis, Advisory Skills, Documentation, Communication'
                }
            ],

            'Dental': [
                {
                    'title': 'General Dentist',
                    'description': 'Provides primary dental care and basic dental procedures',
                    'average_salary': '₹6-20 LPA',
                    'required_skills': 'Clinical Skills, Patient Care, Dental Procedures, Diagnosis'
                },
                {
                    'title': 'Orthodontist',
                    'description': 'Specializes in correcting teeth and jaw alignment',
                    'average_salary': '₹12-35 LPA',
                    'required_skills': 'Orthodontic Procedures, Treatment Planning, Advanced Dental Skills'
                },
                {
                    'title': 'Oral Surgeon',
                    'description': 'Performs complex dental and maxillofacial surgeries',
                    'average_salary': '₹15-45 LPA',
                    'required_skills': 'Surgical Skills, Advanced Procedures, Emergency Care, Critical Care'
                }
            ],

            'Management': [
                {
                    'title': 'Business Manager',
                    'description': 'Oversees business operations and leads teams',
                    'average_salary': '₹8-25 LPA',
                    'required_skills': 'Business Strategy, Team Management, Operations, Leadership'
                },
                {
                    'title': 'Marketing Manager',
                    'description': 'Develops and implements marketing strategies',
                    'average_salary': '₹7-20 LPA',
                    'required_skills': 'Marketing Strategy, Digital Marketing, Brand Management, Analytics'
                },
                {
                    'title': 'Financial Manager',
                    'description': 'Manages financial operations and strategy',
                    'average_salary': '₹10-30 LPA',
                    'required_skills': 'Financial Analysis, Risk Management, Investment Planning, Business Acumen'
                }
            ],

            'Pharmacy': [
                {
                    'title': 'Clinical Pharmacist',
                    'description': 'Works in healthcare settings providing pharmaceutical care',
                    'average_salary': '₹5-15 LPA',
                    'required_skills': 'Clinical Pharmacy, Patient Care, Drug Knowledge, Healthcare Protocols'
                },
                {
                    'title': 'Research Pharmacist',
                    'description': 'Conducts pharmaceutical research and drug development',
                    'average_salary': '₹8-20 LPA',
                    'required_skills': 'Research Methods, Drug Development, Laboratory Skills, Data Analysis'
                },
                {
                    'title': 'Pharmacy Manager',
                    'description': 'Manages pharmacy operations and staff',
                    'average_salary': '₹7-18 LPA',
                    'required_skills': 'Pharmacy Operations, Team Management, Inventory Control, Regulatory Compliance'
                }
            ]
        }

        for field_name, roles in career_roles.items():
            try:
                career_field = CareerField.objects.get(name=field_name)
                self.stdout.write(f'Populating roles for {field_name}...')
                
                for role_data in roles:
                    job_role, created = JobRole.objects.get_or_create(
                        title=role_data['title'],
                        career_field=career_field,
                        defaults={
                            'description': role_data['description'],
                            'average_salary': role_data['average_salary'],
                            'required_skills': role_data['required_skills']
                        }
                    )
                    if created:
                        self.stdout.write(f'Created role: {role_data["title"]}')
                    else:
                        self.stdout.write(f'Updated role: {role_data["title"]}')
                
            except CareerField.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Career field {field_name} not found')
                )
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {field_name}: {str(e)}')
                )
                continue

        self.stdout.write(self.style.SUCCESS('Successfully populated all job roles'))