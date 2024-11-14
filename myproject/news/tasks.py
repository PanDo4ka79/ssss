from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import Category
from datetime import timedelta
from django.utils import timezone
from datetime import datetime


@shared_task
def send_weekly_updates():
    last_week = timezone.now() - timedelta(days=7)
    categories = Category.objects.all()
    for category in categories:
        subscribers = category.subscribers.all()
        new_posts = category.post_set.filter(created_at__gte=last_week)
        if new_posts.exists():
            for user in subscribers:
                post_links = "\n".join([f"{settings.SITE_URL}{reverse('post_detail', args=[post.id])}" for post in new_posts])
                send_mail(
                    subject=f'Еженедельное обновление статей в категории {category.name}',
                    message=f'Вот новые статьи за последнюю неделю:\n{post_links}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

@shared_task
def my_periodic_task():
    print(f"Задача выполнена в {datetime.now()}")