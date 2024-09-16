import os
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models

class ProcessedImage(models.Model):
    image = models.ImageField(upload_to='processed_images/')
    created_at = models.DateTimeField(auto_now_add=True)

def get_image_path(instance, filename):
    return os.path.join('img', filename)

class MyImage(models.Model):
    title = models.CharField(max_length=255, blank=True, verbose_name='Название')
    image = models.ImageField(upload_to=get_image_path, verbose_name='Изображение')

    def __str__(self):
        return self.title

@receiver(pre_save, sender=MyImage)
def set_image_title(sender, instance, **kwargs):
    if not instance.title:
        instance.title = os.path.splitext(os.path.basename(instance.image.name))[0]



class Feedback(models.Model):
    name = models.CharField(max_length=120, verbose_name='Имя')
    email = models.EmailField(max_length=254, verbose_name='Почта')
    topic_options = [('o1', 'Общие вопросы/комментарии'), ('o2','Техническая проблема')]
    topic = models.CharField(max_length=2, choices=topic_options, blank=False, default='o1', verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')

    def __str__(self):
        return self.name
    