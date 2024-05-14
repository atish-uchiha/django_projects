from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from product.models import ProductTable,CartTable
from django.db.models import Q
from django.contrib import messages


def user_login(request):
  data = {}
  if request.user.is_authenticated:
    if request.user.is_superuser:
      return redirect('/admin')
    else:
      return redirect('/')

  if request.method == 'POST':
    uname = request.POST['username']
    upass = request.POST['password']
    if(uname=='' or upass==''):
     data['error_msg'] = "*Please fill all fields*"
     
    elif(not User.objects.filter(username=uname).exists()):
     data['error_msg'] = uname + " Does not exists!"
    else:
     user = authenticate(username=uname, password=upass)
     print(user)
     if user is None:
      data['error_msg'] = "Invalid Password"
     else:
      login(request,user)
      if user.is_superuser:
        return redirect('/admin')
      else:
        return redirect("/")
  return render(request,'user/login.html',context=data)


def user_register(request):
   data = {}
   if request.user.is_authenticated:
    if request.user.is_superuser:
      return redirect('/admin')
    else:
      return redirect('/')

   if request.method == 'POST':
    uname = request.POST['username']
    upass = request.POST['password']
    uconf_pass = request.POST['password2']
    if(uname=='' or upass=='' or uconf_pass==''):
     data['error_msg'] = "*Please fill all fields*"
    elif(upass != uconf_pass):
     data['error_msg'] = "Passwords do not match"
    elif(User.objects.filter(username=uname).exists()):
     data['error_msg'] = uname + " Username already exists!"
    else:
     new_user = User.objects.create(username=uname)
     new_user.set_password(upass) #encrypt the password before saving it in db
     new_user.save()
     return redirect("/")
   return render(request,'user/register.html',context=data)

def user_logout(request):
  logout(request)
  return redirect('/')

def admin_panel(request):
  if request.user.is_authenticated:
    if not request.user.is_superuser:
      return redirect('/')  
  return render(request,'admin/admin.html')

#---------------------------All Logics----------------------------

products=ProductTable.objects.none()
def  home(request):
    data = {}
    global products
    global filtered_products
    products = ProductTable.objects.filter(is_available=True)
    filtered_products = products
    data['products'] = products
    #getting cart count specific to logged in user
    user_id = request.user.id
    cart = CartTable.objects.filter(uid=user_id)
    data['cartvalue'] = cart.count()
    return render(request,'base.html',context=data)

def filter_by_category(request,category_value):
  data = {}
  #Select * from product where is_available=True and category=category_value
  #from django.db.models import Q--------->queryset
  q1 = Q(is_available=True)
  q2 = Q(category=category_value)
  global products
  global filtered_products
  filtered_products = products.filter(q1 & q2)
  data['products']=filtered_products
  return render(request,'base.html',context=data)

def sort_by_price(request,sort_value):
  data = {}
  global filtered_products
  # select * from product where is_available=True order by price desc
  if(sort_value=='asc'):
    sorted_products=filtered_products.filter(is_available=True).order_by('price')
  else:
    sorted_products=filtered_products.filter(is_available=True).order_by('-price')
  data['products']=sorted_products
  return render(request,"base.html",context=data)

def search_by_price_range(request):
  data = {}
  min = request.POST['min']
  max = request.POST['max']
  q1 = Q(is_available=True)
  q2 = Q(price__gte=min)
  q3 = Q(price__lte=max)
  searched_products = filtered_products.filter(q1 & q2 & q3)
  data["products"] = searched_products
  return render(request,'base.html',context=data)

def add_to_cart(request,product_id):
  if request.user.is_authenticated:
    user = request.user
    product = ProductTable.objects.get(id=product_id)
    q1 = Q(uid=request.user.id)
    q2 = Q(pid=product.id)
    cart_value = CartTable.objects.filter(q1 & q2)
    if(cart_value.count()>0):
      messages.error(request,'Product is already in the cart')
    else:
      cart = CartTable.objects.create(uid=user,pid=product,quantity=1)
      cart.save()
      messages.success(request,'Added to cart successfully!')
    return redirect('/')
  else:
    return redirect('/login')

def find_cart_value(request):
  user_id = request.user.id
  cart = CartTable.objects.filter(uid=user_id)
  cart_count = cart.count()
  return cart_count
  
def show_cart(request):
  data = {}
  total_items=0
  total_price=0
  cart_count = find_cart_value(request)
  data['cartvalue'] = cart_count
  products_in_cart = CartTable.objects.filter(uid=request.user.id)
  data['cartproducts'] = products_in_cart
  for product in products_in_cart:
    total_items += product.quantity
    total_price += (  product.pid.price*product.quantity)
    data['total_items'] = total_items
    data['total_price'] = total_price
  return render(request,"home/show_cart.html",context=data)

def delete_cart(request,cart_id):
  cart = CartTable.objects.get(id=cart_id)
  cart.delete()
  return redirect("/cart")

def update_cart_quantity(request,flag,cart_id):
  cart = CartTable.objects.filter(id=cart_id)
  actual_quantity = cart[0].quantity
  if flag == 'inc':
    cart.update(quantity=actual_quantity+1)
  else:
    if(cart[0].quantity==1):
      pass
    else:
      cart.update(quantity=actual_quantity-1)
  return redirect("/cart")

     
def show_order(request):
  data = {}
  total_items=0
  total_price=0
  cart_count = find_cart_value(request)
  data['cartvalue'] = cart_count
  products_in_cart = CartTable.objects.filter(uid=request.user.id)
  data['cartproducts'] = products_in_cart
  for product in products_in_cart:
    total_items += product.quantity
    total_price += (  product.pid.price*product.quantity)
    data['total_items'] = total_items
    data['total_price'] = total_price
  return render(request,"home/show_order.html",context=data)


import razorpay
def make_payment(request):
  
  total_price=0
  products_in_cart=CartTable.objects.filter(uid=request.user.id)
  for product in products_in_cart:
    total_price+=(product.pid.price*product.quantity)
   

  client = razorpay.Client(auth=("rzp_test_p7S3hv6Om8f97W", "tkq7Dx8ePraESwpXMS5MEvdQ"))
  data = { "amount": total_price*100, "currency": "INR", "receipt": "order_rcptid_11" }
  payment = client.order.create(data=data)
  print(payment)
  return render(request,'home/pay.html',context=data)

