
// var modal = document.getElementById("myModal");

// // Получаем кнопку, которая открывает модальное окно
// var btn = document.getElementById("myBtn");

// // Получаем элемент <span>, который закрывает модальное окно
// var span = document.getElementsByClassName("close")[0];

// // Когда пользователь кликает на кнопку, открываем модальное окно 
// btn.onclick = function() {
//   modal.style.display = "block";
// }

// // Когда пользователь кликает на <span> (x), закрываем модальное окно
// span.onclick = function() {
//   modal.style.display = "none";
// }

// // Когда пользователь кликает в любом месте вне модального окна, закрываем его
// window.onclick = function(event) {
//   if (event.target == modal) {
//     modal.style.display = "none";
//   }
// }

// // Функция для загрузки фотографии
// function uploadPhotos() {
//     var form = document.getElementById("upload-form");
//     var formData = new FormData(form);
    
//     $.ajax({
//         url: form.action,
//         type: form.method,
//         data: formData,
//         processData: false,
//         contentType: false,
//         success: function(data) {
//             // Обработка успешного ответа от сервера (например, обновление страницы для отображения загруженных изображений)
//             window.location.reload();
//         },
//         error: function(xhr, status, error) {
//             // Обработка ошибки
//             console.error(xhr.responseText);
//         }
//     });
// }



