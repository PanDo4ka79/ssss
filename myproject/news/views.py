from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, User, Category, Subscription
from django.core.paginator import Paginator
from django_filters import rest_framework as filters
from django.forms import DateInput
from .filters import PostFilter
from django.urls import  reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages



def news_list(request):
    news = Post.objects.filter(category_type=Post.NEWS).order_by('-created_at')
    return render(request, 'news/news_list.html', {'news': news})


def news_detail(request, pk):
    news = get_object_or_404(Post, pk=pk, category_type=Post.NEWS)
    return render(request, 'news/news_detail.html', {'news': news})


def news_list2(request):
    news = Post.objects.all().order_by('-created_at')
    paginator = Paginator(news, 10)  # 10 новостей на страницу

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {'page_obj': page_obj})


class PostFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    author__user__username = filters.CharFilter(lookup_expr='icontains', label='Автор')
    created_at = filters.DateFilter(widget=DateInput(attrs={'type': 'date'}), lookup_expr='gte', label='Позже даты')

    class Meta:
        model = Post
        fields = ['title', 'author__user__username', 'created_at']


def news_search(request):
    post_filter = PostFilter(request.GET, queryset=Post.objects.all())
    return render(request, 'news/news_search.html', {'filter': post_filter})

class PostCreateView(CreateView, UserPassesTestMixin):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'
    success_url = reverse_lazy('news_list')
    fields = ['title', 'content', 'categories']

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'
    success_url = reverse_lazy('news_list')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'news/post_confirm_delete.html'
    success_url = reverse_lazy('news_list')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User  # Укажите свою модель профиля
    template_name = 'profile_edit.html'
    fields = ['first_name', 'last_name', 'email']
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        return self.request.user.profile

@login_required
def become_author(request):
    author_group, _ = Group.objects.get_or_create(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        request.user.groups.add(author_group)
    return redirect('profile')

class PostEditView(UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'post_form.html'
    fields = ['title', 'content', 'categories']

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    Subscription.objects.get_or_create(user=request.user, category=category)
    messages.success(request, f'Вы подписались на категорию "{category.name}"')
    return redirect('category_detail', category_id=category.id)