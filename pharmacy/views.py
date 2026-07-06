from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Medicine, Cart, CartItem, Order, OrderItem

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

def medicine_list(request, category_id=None):
    categories = Category.objects.all()
    medicines = Medicine.objects.all()
    active_category = None
    
    if category_id:
        active_category = get_object_or_404(Category, id=category_id)
        medicines = medicines.filter(category=active_category)
        
    context = {
        'categories': categories,
        'medicines': medicines,
        'active_category': active_category
    }
    return render(request, 'pharmacy/medicine_list.html', context)

def medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    return render(request, 'pharmacy/medicine_detail.html', {'medicine': medicine})

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'pharmacy/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, medicine_id):
    if request.method == 'POST':
        medicine = get_object_or_404(Medicine, id=medicine_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Basic stock check
        if quantity > medicine.stock:
            messages.error(request, f"Only {medicine.stock} units available.")
            return redirect('pharmacy:medicine_detail', medicine_id=medicine.id)
            
        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, medicine=medicine)
        
        if not created:
            if cart_item.quantity + quantity > medicine.stock:
                messages.error(request, f"Cannot add more. Only {medicine.stock} total units available.")
            else:
                cart_item.quantity += quantity
                cart_item.save()
                messages.success(request, f"Updated {medicine.name} quantity in your cart.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Added {medicine.name} to your cart.")
            
    return redirect('pharmacy:cart_view')

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            if quantity > cart_item.medicine.stock:
                messages.error(request, f"Only {cart_item.medicine.stock} units available.")
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
            
    return redirect('pharmacy:cart_view')

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    return redirect('pharmacy:cart_view')

@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('pharmacy:medicine_list')
        
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        if not shipping_address:
            messages.error(request, "Please provide a shipping address.")
            return redirect('pharmacy:checkout')
            
        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            shipping_address=shipping_address,
            status='Pending'
        )
        
        # Create Order Items and update stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine,
                price=item.medicine.price,
                quantity=item.quantity
            )
            # Decrease stock
            item.medicine.stock -= item.quantity
            item.medicine.save()
            
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('pharmacy:order_history')
        
    return render(request, 'pharmacy/checkout.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pharmacy/order_history.html', {'orders': orders})
