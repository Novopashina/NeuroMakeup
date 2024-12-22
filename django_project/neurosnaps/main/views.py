from django.shortcuts import render
from django.http import JsonResponse
from .models import ProcessedImage
from .models import MyImage
from .forms import ImageForm
from .forms import FeedbackForm
import requests
from django.shortcuts import render
import requests
from django.core.files.base import ContentFile


def image_upload_view(request):
    img_obj1 = None
    img_obj2 = None

    if request.method == 'POST':
        form1 = ImageForm(request.POST, request.FILES, prefix='form1')
        form2 = ImageForm(request.POST, request.FILES, prefix='form2')
        
        if form1.is_valid() and form2.is_valid():
            img_obj1 = form1.save()
            img_obj2 = form2.save()

    else:
        form1 = ImageForm(prefix='form1')
        form2 = ImageForm(prefix='form2')

    return render(request, 'home.html', {'form1': form1, 'form2': form2, 'img_obj1': img_obj1, 'img_obj2': img_obj2})

def apply_transformation(request):
    if request.method == 'POST':
        img_obj1 = request.FILES['img_obj1']
        img_obj2 = request.FILES['img_obj2']
        serv_url = 'http://localhost:8080/process_images'  # здесь localhost заменить на доменное имя ?сервера с нейросетью?
        files = {'image1': img_obj1, 'image2': img_obj2}
        response = requests.post(serv_url, files=files)

        if response.status_code == 200:
            processed_image = ProcessedImage()
            processed_image.image.save('processed.jpeg', ContentFile(response.content))
            image1 = MyImage.objects.create(image=img_obj1)
            image2 = MyImage.objects.create(image=img_obj2)
            image_path = processed_image.image.url

            return JsonResponse({'image_path': image_path})
        else:
            return render(request, 'home.html')
    else:
        return render(request, 'home.html')


def feedback_view(request):
    message_sent = False
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            message_sent = True 
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form, 'message_sent': message_sent})



