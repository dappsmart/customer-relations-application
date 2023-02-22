from django.shortcuts import render, redirect
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group


# Create your views here.

@unauthenticated_user
def registerPage(request):
    
    
    form = CreateUserForm()    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user, name=username, email=user.email,
                )
            
            messages.success(request, 'Account has been created for' + username) 
            
            return redirect('login')

    
    context = {'form': form}
    
    return render(request, 'accounts/register.html', context)
    




    
@unauthenticated_user   
def loginPage(request):
     
    
           
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)                
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')

            
    context = {}
    
    return render(request, 'accounts/login.html', context)



def logoutUser(request):

    logout(request)
    
    return redirect('login')




@login_required(login_url='login')
@admin_only

def home(request):
    
    orders = Order.objects.all()
    customers = Customer.objects.all()
    
    total_orders = orders.count()
    total_customers = customers.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
 
    
    context = {'orders': orders, 'customers': customers, 'pending': pending, 'total_orders': total_orders, 'total_customers': total_customers, 'delivered': delivered}
    
    return render(request, 'accounts/dAshboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    
    orders = request.user.customer.order_set.all()
    customer = request.user.customer
    
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    print ('SIPARISLER:',orders)
    
    context = {'customer': customer, 'orders': orders, 'myFilter': myFilter, 'pending': pending, 'total_orders': total_orders, 'delivered': delivered}
    return render(request, 'accounts/user.html', context)




@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    
    
    context={'form':form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    
    context = { 'customer': customer, 'orders': orders, 'order_count' : order_count, 'myFilter': myFilter }
    
    
    return render(request, 'accounts/cuStoMer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
        
    return render(request, 'accounts/prOduCts.html', {'products': products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def status(request):
    
    orders = Order.objects.all()
    
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    
    
    context = {'orders': orders, 'pending': pending, 'total_orders': total_orders, 'delivered': delivered}

    
    return render(request, 'accounts/stAtus.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    
    
    customer = Customer.objects.get(id=pk)
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    formset = OrderFormSet(instance=customer, queryset=Order.objects.none())
    
    form = OrderForm(initial={'customer': customer})
    
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    
    context = {'form':form, 'customer':customer, 'OrderFormSet':OrderFormSet, 'formset':formset}
        
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):    
    
    order = Order.objects.get(id=pk)
    formset = OrderForm(instance=order)
    
    
    if request.method == 'POST':
        formset = OrderForm(request.POST, instance=order)
    
        if formset.is_valid():
            formset.save()
            return redirect('/')
    
    
    context = {'formset':formset, 'order':order}
        
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    
    
    order = Order.objects.get(id=pk)
    
    
    if request.method == 'POST':       
    
        
        order.delete()
        return redirect('/')
        
        
    context = {'item':order}
        
    return render(request, 'accounts/delete.html', context)


