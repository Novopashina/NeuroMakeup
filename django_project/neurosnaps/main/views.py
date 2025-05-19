from django.shortcuts import render
from django.http import JsonResponse
from .models import ProcessedImage
from .models import MyImage
from .forms import ImageForm
from .forms import FeedbackForm
import requests
from django.shortcuts import render
from django.core.files.base import ContentFile


def images_upload_view(request):
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
        img_obj1 = request.FILES['img_obj1'] # получаем 2 изображения для отправки
        img_obj2 = request.FILES['img_obj2']
        # serv_url = 'http://localhost:8080/process_images'
        serv_url = 'http://makeapp-server-anaesthesia.amvera.io/process_images'  # здесь localhost заменить на доменное имя ?сервера с нейросетью?
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
    
def image_upload(request):
    img_obj1 = None

    if request.method == 'POST':
        form1 = ImageForm(request.POST, request.FILES, prefix='form1')
        
        if form1.is_valid():
            img_obj1 = form1.save()

    else:
        form1 = ImageForm(prefix='form1')

    return render(request, 'recogn.html', {'form1': form1, 'img_obj1': img_obj1})


def detect_emotion(request):
    if request.method == 'POST' and request.FILES.get('img_obj1'):
        # url = "http://127.0.0.1:8081"  
        
        url = "http://emotapp-server-anaesthesia.amvera.io"
        files = {'image': request.FILES['img_obj1']}  # Отправляем файл

        try:
            response = requests.post(url, files=files)
            # print("Status code:", response.status_code)
            # print("Response content:", response.content)
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    return JsonResponse({'error': 'Ответ сервера не в JSON-формате'}, status=500)

                user_emotion = data.get('user_emotion', 'Не определено')
                matching_image = data.get('matching_image', '')

                return JsonResponse({
                    'user_emotion': user_emotion,
                    'matching_image': f"/static/img/{matching_image}" if matching_image else ""
                })
            else:
                return JsonResponse({'error': 'Ошибка обработки на сервере'}, status=500)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Ошибка соединения: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Неверный запрос'}, status=400)



# def detect_emotion(request):
#     user_emotion = None
#     matching_image = None
#     img_obj = None

#     if request.method == 'POST':
#         form = ImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             img_obj = form.save()
#             img_path = img_obj.image.path

#             with open(img_path, 'rb') as img_file:
#                 image_data = img_file.read()

#             serv_url = 'http://localhost:8080'  # URL сервера
#             # response = requests.post(serv_url, json={'image': image_data.decode('latin1')})
#             response = requests.post(serv_url, files={'image': image_data})


#             if response.status_code == 200:
#                 data = response.json()
#                 user_emotion = data.get('user_emotion', 'Неизвестно')
#                 matching_image = data.get('matching_image', None)
            
#     else:
#         form = ImageForm()

#     return render(request, 'recogn.html', {
#         'form': form,
#         'img_obj': img_obj,
#         'user_emotion': user_emotion,
#         'matching_image': matching_image
#     })


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



