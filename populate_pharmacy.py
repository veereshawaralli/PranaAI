import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medibuddy_project.settings')
django.setup()

from pharmacy.models import Category, Medicine

def populate():
    print("Clearing old data...")
    Medicine.objects.all().delete()
    Category.objects.all().delete()

    print("Creating categories...")
    pain_relief, _ = Category.objects.get_or_create(name="Pain Relief", description="Medicines for pain management")
    first_aid, _ = Category.objects.get_or_create(name="First Aid", description="Bandages, antiseptics, and wound care")
    vitamins, _ = Category.objects.get_or_create(name="Vitamins & Supplements", description="Daily vitamins for health")
    cold_flu, _ = Category.objects.get_or_create(name="Cold & Flu", description="Relief for cold, cough, and flu symptoms")

    print("Creating medicines...")
    medicines = [
        {
            "category": pain_relief,
            "name": "Paracetamol 500mg",
            "description": "Used to treat mild to moderate pain and reduce fever.",
            "price": 25.00,
            "stock": 100,
            "requires_prescription": False
        },
        {
            "category": pain_relief,
            "name": "Ibuprofen 400mg",
            "description": "Nonsteroidal anti-inflammatory drug (NSAID) used for pain relief and fever reduction.",
            "price": 45.50,
            "stock": 50,
            "requires_prescription": True
        },
        {
            "category": first_aid,
            "name": "Antiseptic Liquid (Dettol) 250ml",
            "description": "Antiseptic liquid for first aid, medical and personal hygiene uses.",
            "price": 120.00,
            "stock": 30,
            "requires_prescription": False
        },
        {
            "category": vitamins,
            "name": "Vitamin C 1000mg",
            "description": "Immunity booster supplement.",
            "price": 250.00,
            "stock": 200,
            "requires_prescription": False
        },
        {
            "category": cold_flu,
            "name": "Cough Syrup 100ml",
            "description": "Relief from dry and wet cough.",
            "price": 85.00,
            "stock": 40,
            "requires_prescription": False
        }
    ]

    for med_data in medicines:
        Medicine.objects.create(**med_data)

    print("Successfully populated the Pharmacy database with dummy data!")

if __name__ == '__main__':
    populate()
