from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = "Добро пожаловать на наш сайт!"
        message = f"Привет, {instance.username}! Спасибо за регистрацию на нашем сайте."
        recipient_list = [instance.email]
        send_mail(subject, message, 'your_email@gmail.com', recipient_list)  # Отправляем почту
