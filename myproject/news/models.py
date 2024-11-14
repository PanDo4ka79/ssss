from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings



class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_ratings = self.post_set.aggregate(postRating=models.Sum('rating'))
        post_sum = post_ratings.get('postRating') or 0

        comment_ratings = self.user.comment_set.aggregate(commentRating=models.Sum('rating'))
        comment_sum = comment_ratings.get('commentRating') or 0

        post_comments_ratings = Comment.objects.filter(post__author=self).aggregate(
            commentPostRating=models.Sum('rating'))
        post_comment_sum = post_comments_ratings.get('commentPostRating') or 0

        self.rating = post_sum * 3 + comment_sum + post_comment_sum
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, through='Subscription', related_name='subscribed_categories')

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = [
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    ]

    category_type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    if created:
        common_group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)

def ready(self):
    import signals

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        category = instance.category
        subscribers = category.subscribers.all()
        for user in subscribers:
            send_mail(
                subject=f'Новая статья в категории {category.name}',
                message=f'Прочитайте новую статью "{instance.title}": {settings.SITE_URL}{reverse("post_detail", args=[instance.id])}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )