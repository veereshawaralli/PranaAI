import os
import django
import random
import urllib.request
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medibuddy_project.settings')
django.setup()

from pharmacy.models import Medicine

def main():
    medicines = Medicine.objects.all()
    count = 0
    print(f"Fetching random medicine images for {medicines.count()} products...")
    
    for med in medicines:
        try:
            # We use a random lock number to ensure we get a unique image from loremflickr each time
            lock = random.randint(1, 10000)
            url = f'https://loremflickr.com/320/240/medicine,pill?lock={lock}'
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                image_data = response.read()
                
            # Create a valid filename for the model
            safe_name = "".join([c if c.isalnum() else "_" for c in med.name]).strip("_")[:50]
            filename = f"{safe_name}_{lock}.jpg"
            
            # Save the downloaded image directly to the ImageField
            med.image.save(filename, ContentFile(image_data), save=True)
            print(f"Assigned image to {med.name}")
            count += 1
        except Exception as e:
            print(f"Failed to fetch image for {med.name}: {e}")
            
    print(f"\nSuccessfully downloaded and assigned real placeholder images to {count} medicines.")

if __name__ == '__main__':
    main()
