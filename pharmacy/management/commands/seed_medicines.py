import json
import random
import urllib.request
from django.core.management.base import BaseCommand
from pharmacy.models import Category, Medicine

class Command(BaseCommand):
    help = 'Seeds the database with medicines from openFDA API'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching data from openFDA API...')
        url = 'https://api.fda.gov/drug/label.json?search=openfda.product_type:%22HUMAN%20OTC%20DRUG%22&limit=50'
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
        except Exception as e:
            self.stderr.write(f"Error fetching data: {e}")
            return
            
        results = data.get('results', [])
        
        if not results:
            self.stderr.write("No results found in API response.")
            return

        # Default categories to fall back to
        default_categories = ["Pain Relief", "Cold & Flu", "Allergy", "Digestive Health", "First Aid", "Vitamins"]
        for cat_name in default_categories:
            Category.objects.get_or_create(name=cat_name, defaults={'description': f'Various {cat_name} products.'})
            
        categories = list(Category.objects.all())
        
        count = 0
        for item in results:
            openfda = item.get('openfda', {})
            
            # Extract basic information
            brand_name = openfda.get('brand_name', [])
            generic_name = openfda.get('generic_name', [])
            
            name = ""
            if brand_name:
                name = brand_name[0]
            elif generic_name:
                name = generic_name[0]
            else:
                continue
                
            # Truncate name if it's too long
            name = name[:200].title()
            
            description = ""
            if item.get('description'):
                description = item['description'][0]
            elif item.get('indications_and_usage'):
                description = item['indications_and_usage'][0]
            else:
                description = f"Generic {name}."
                
            description = description[:1000]
            
            # Select category based on pharm class if available, else random
            pharm_class = openfda.get('pharm_class_cs', [])
            if pharm_class:
                cat_name = pharm_class[0][:100]
                category, _ = Category.objects.get_or_create(name=cat_name)
            else:
                category = random.choice(categories)
                
            # Randomize price and stock since API doesn't provide them
            price = round(random.uniform(5.0, 150.0), 2)
            stock = random.randint(10, 500)
            requires_prescription = False # OTC drugs usually don't require
            
            # Add or update medicine
            Medicine.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'price': price,
                    'stock': stock,
                    'requires_prescription': requires_prescription
                }
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added/updated {count} medicines!'))
