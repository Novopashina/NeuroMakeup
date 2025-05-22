import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .models import ProcessedImage
from .models import MyImage
from .forms import ImageForm
from .forms import FeedbackForm
import requests
from django.shortcuts import render
from django.core.files.base import ContentFile
from PIL import Image
import numpy as np
import cv2
import requests
from io import BytesIO
from django.utils.crypto import get_random_string


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

def images_upload_ajax(request):
    if request.method == 'POST':
        try:
            processed_image1 = None
            processed_image2 = None
            if request.FILES.get('img_obj1'):
                processed_content1 = process_image_opencv(request.FILES['img_obj1'])
                processed_image1 = ProcessedImage()
                processed_image1.image.save(f'processed1_{get_random_string(8)}.jpg', processed_content1)
            if request.FILES.get('img_obj2'):
                processed_content2 = process_image_opencv(request.FILES['img_obj2'])
                processed_image2 = ProcessedImage()
                processed_image2.image.save(f'processed2_{get_random_string(8)}.jpg', processed_content2)

            return JsonResponse({
                'processed_image_url1': processed_image1.image.url if processed_image1 else '',
                'processed_image_url2': processed_image2.image.url if processed_image2 else ''
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def apply_transformation(request):
    if request.method == 'POST':
        img_path1 = request.POST.get('img_path1')
        img_path2 = request.POST.get('img_path2')
        source = request.POST.get('source')  

        if not img_path1 or not img_path2:
            return JsonResponse({'error': 'Пути изображений не переданы.'}, status=400)
        img_path1 = os.path.join(settings.MEDIA_ROOT, img_path1.replace('/media/', ''))

        if source == 'recogn':
            relative_path = img_path2.replace(settings.STATIC_URL, '')  
            img_path2 = os.path.join(settings.STATICFILES_DIRS[0], relative_path)
        else:
            img_path2 = os.path.join(settings.MEDIA_ROOT, img_path2.replace('/media/', ''))


        try:
            with open(img_path1, 'rb') as f1, open(img_path2, 'rb') as f2:
                files = {
                    'image1': f1,
                    'image2': f2,
                }
                serv_url = 'http://makeapp-server-anaesthesia.amvera.io/process_images'
                response = requests.post(serv_url, files=files)

            if response.status_code == 200:
                processed_image = ProcessedImage()
                processed_image.image.save('processed.jpeg', ContentFile(response.content))
                image_path = processed_image.image.url
                return JsonResponse({'image_path': image_path})
            else:
                return JsonResponse({'error': 'Ошибка на сервере обработки.'}, status=500)
        except FileNotFoundError as e:
            return JsonResponse({'error': f'Файл не найден: {str(e)}'}, status=500)
    
    return render(request, 'home.html')

# def apply_transformation(request):
#     if request.method == 'POST':
#         img_obj1 = request.FILES['img_obj1'] # получаем 2 изображения для отправки
#         img_obj2 = request.FILES['img_obj2']
#         # serv_url = 'http://localhost:8080/process_images'
#         serv_url = 'http://makeapp-server-anaesthesia.amvera.io/process_images'  # здесь localhost заменить на доменное имя ?сервера с нейросетью?
#         files = {'image1': img_obj1, 'image2': img_obj2}
#         response = requests.post(serv_url, files=files)

#         if response.status_code == 200:
#             processed_image = ProcessedImage()
#             processed_image.image.save('processed.jpeg', ContentFile(response.content))
#             image1 = MyImage.objects.create(image=img_obj1)
#             image2 = MyImage.objects.create(image=img_obj2)
#             image_path = processed_image.image.url

#             return JsonResponse({'image_path': image_path})
#         else:
#             return render(request, 'home.html')
#     else:
#         return render(request, 'home.html')
    
def process_image_opencv(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    open_cv_image = np.array(img)[:, :, ::-1].copy()

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        raise ValueError("Лицо не найдено")

    x, y, w, h = faces[0]
    h_img, w_img, _ = open_cv_image.shape
    x1 = max(x - 600, 0)
    y1 = max(y - 600, 0)
    x2 = min(x + w + 600, w_img)
    y2 = min(y + h + 600, h_img)

    cropped = open_cv_image[y1:y2, x1:x2]
    pil_image = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    width, height = pil_image.size
    min_side = min(width, height)
    left_crop = (width - min_side) // 2
    top_crop = (height - min_side) // 2
    square_image = pil_image.crop((left_crop, top_crop, left_crop + min_side, top_crop + min_side))

    final_image = square_image.resize((361, 361), Image.LANCZOS)
    buffer = BytesIO()
    final_image.save(buffer, format='JPEG')
    buffer.seek(0)
    return ContentFile(buffer.read(), name='processed.jpg')

def image_upload(request):
    if request.method == 'POST' and request.FILES.get('img_obj1'):
        try:
            processed_content = process_image_opencv(request.FILES['img_obj1'])
            processed_image = ProcessedImage()
            processed_image.image.save('processed_user.jpg', processed_content)

            return JsonResponse({
                'processed_image_url': processed_image.image.url})
        except Exception as e:
            return JsonResponse({'error': f'Ошибка обработки изображения: {str(e)}'}, status=500)
    form = ImageForm()
    return render(request, 'recogn.html', {'form1': form})

def detect_emotion(request):
    if request.method == 'POST' and request.FILES.get('img_obj1'):
        url = "http://emotapp-server-anaesthesia.amvera.io"
        files = {'image': request.FILES['img_obj1']}  
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
                    'matching_image': f"/static/img/{matching_image}" if matching_image else ""})
            else:
                return JsonResponse({'error': 'Ошибка обработки на сервере'}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Ошибка соединения: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Неверный запрос'}, status=400)



# def image_upload(request):
#     img_obj1 = None

#     if request.method == 'POST':
#         form1 = ImageForm(request.POST, request.FILES, prefix='form1')
        
#         if form1.is_valid():
#             img_obj1 = form1.save()

#     else:
#         form1 = ImageForm(prefix='form1')

#     return render(request, 'recogn.html', {'form1': form1, 'img_obj1': img_obj1})


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



