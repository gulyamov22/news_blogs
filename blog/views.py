from django.shortcuts import render, redirect
from .models import Post, Category, Comment
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterFrom
from django.urls import reverse

def index(request):
    posts = Post.objects.order_by('-date')[:10]
    recommendations = Post.objects.filter(view__gte=100)[:3]
    categoies = Category.objects.all()
    context =  {'posts': posts, 
                'categories': categoies,
                'recommendations': recommendations }
    return render(request, 'index.html', context)

def post_detail(request, slug):
    post = Post.objects.get(slug__exact=slug)
    post.view += 1
    post.save()
    return render(request, 'post_detail.html', {'post':post})

def category_detail(request, slug):
     category = Category.objects.get(slug__exact=slug)
     return render(request, 'category_detail.html', {'category':category})

def search(request):
    query = request.GET.get('search')
    posts =Post.objects.filter(Q(title__iregex = query))
    content ={ 'posts': posts, "query":query}
    return render(request, 'search.html', 'context')

def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegisterFrom(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('index')
        else:
            form = RegisterFrom()
        return render(request, 'register.html', {'form': form})
    return redirect('index')


def login_site(request):
    if request.user.is_authenticated:
        return redirect('index')
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'login.html', {'message':message})
    return render(request, 'login.html', {'message':message})

def logout_site(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

def comment(request, slug):
    post = Post.objects.get(slug__exact=slug)
    if request.method == 'POST':
        comment = Comment()
        comment.author = request.user
        comment.post = Post.objects.get(slug__exact=slug)
        comment.text = request.POST.get('text')
        if not comment.text:
             return redirect(reverse('post_detail_url', kwargs={'slug' : post.slug}))
        comment.save()
        return redirect(reverse('post_detail_url', kwargs={'slug' : post.slug}))
    return redirect(reverse('post_detail_url', kwargs={'slug' : post.slug}))