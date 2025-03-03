from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q 
import json
from cart.cart import Cart 

def search(request):
    #Determine if they fiiled out the form
    if request.method == "POST":
        searched = request.POST['searched'] 
        # Query the product db model
        searched = Product.objects.filter(Q(name__icontains = searched) | Q(description__icontains = searched))
        # Test null
        if  not searched:
            messages.success(request, "No Result....")
            return render(request, 'search.html',{})
        else:
            return render(request, 'search.html',{'searched':searched})
    else:
        return render(request, 'search.html',{})


def update_info(request):
    if request.user.is_authenticated:
        #Get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        # Get current user's shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        #Get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #Get User Original Shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            # Save original form 
            form.save()
            shipping_form.save()
            #Save the shiiping form
            messages.success(request, "Your Info Has Been Updated....")
            return redirect('home')
        return render(request, 'update_info.html',{'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request, "You Must Be Login To Update")
        return redirect('home')




def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
    #Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user,request.POST)
            #Check If the  it is Valid
            if form.is_valid():
                form.save()
                messages.success(request,"Your Password Has Been Updated... ")
                login(request,current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html',{'form':form})
    
    else:
        messages.success(request, "You Need To Login")
        return redirect('home')


def update_user(request):
    if  request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        
        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated....")
            return redirect('home')
        return render(request, 'update_user.html',{'user_form':user_form})
    else:
        messages.success(request, "You Must Be Login To Update")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})



def category(request, foo):
    # replace hyphens with sapces
    foo = foo.replace('-', ' ')
    # grab the categoryfrom url
    try:
        # look up the category
        
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category':category})
    except:
        messages.success(request,"category doesn't exist")
        
        return redirect('home')


def product(request,pk):
    product = Product.objects.get(id=pk)
    return render (request, 'product.html', {'product':product})



def home(request):
    products = Product.objects.all()
    return render (request, 'home.html', {'products':products})

def about(request):
    return render (request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            #Do some shopping cart stuff 
            current_user = Profile.objects.get(user__id=request.user.id)
            #Get let the saved cart from DB

            saved_cart = current_user.old_cart
            #Convert DB string to python dictionary
            if saved_cart:
                #Convert to dictionary
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                #Get the cart
                cart = Cart(request)
                # Loop through the cart and add the id items from DB
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)


            messages.success(request,'Welcome Back !!!')
            return redirect('home')

        else:
            messages.success(request,'incorrect login info')
            return redirect('login')
    else:
        return render (request, 'login.html', {})   

def logout_user(request):
    logout(request)
    messages.success(request, ("you've been logged out ......see you soon"))
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data[ 'password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, ("username Created Please Fill Out Your User Info Below!!!"))
            return redirect('update_info')
        else:
            messages.success(request, ("Problem With Your Registration, Please Try Again!"))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
