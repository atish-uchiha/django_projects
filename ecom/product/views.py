from django.shortcuts import render,redirect
from product.models import ProductTable
# Create your views here.

def add_product(request):
  if  request.method == 'POST':
    name = request.POST.get('name')
    price = request.POST.get('price')
    description = request.POST.get('description')
    quantity = request.POST.get('quantity')
    category = request.POST.get('category')
    image = request.FILES.get('image')
    is_available = (request.POST.get('is_available',False))and('is_available' in request.POST)
    product = ProductTable.objects.create(name=name, price=price,description=description,quantity=quantity,category=category,image=image,is_available=is_available)
    product.save()
    return redirect("/admin/product/view")
  return render(request,'admin/product/add_product.html')

def view_product(request):
  data = {}
  all_product = ProductTable.objects.all()
  data['products']=all_product
  return render(request,'admin/product/view_product.html',context=data)

def delete_product(request,pid):
  del_product = ProductTable.objects.get(id=pid)
  del_product.delete()
  return redirect("/admin/product/view")

def update_product(request,pid):
  data = {}
  fetch_product = ProductTable.objects.get(id=pid)
  data['products'] = fetch_product
  if  request.method == 'POST':
    name = request.POST.get('name')
    price = request.POST.get('price')
    description = request.POST.get('description')
    quantity = request.POST.get('quantity')
    category = request.POST.get('category')
    image = request.FILES.get('image')
    is_available = (request.POST.get('is_available',False))and('is_available' in request.POST)
    product = ProductTable.objects.filter(pk=pid)
    product.update(name=name, price=price,description=description,quantity=quantity,category=category,image=image,is_available=is_available)
    return redirect("/admin/product/view")
  return render(request,'admin/product/add_product.html',context=data)


