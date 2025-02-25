window.onload = function() {
    document.getElementById('remember').addEventListener('change', function() {
        var label = document.getElementById('rememberLabel');
        if (this.checked) {
            label.style.color = 'green'; // Цвет, когда чекбокс выбран
        } else {
            label.style.color = 'black'; // Цвет, когда чекбокс не выбран
        }
    });
};

$(document).on('click', '.add-button', function(e) {
    e.preventDefault();

    var product_id = $(this).val(); // Получаем ID продукта из кнопки
    var product_qty = $('#select' + product_id + ' option:selected').val(); // Берём количество из соответствующего select

    $.ajax({
        type: 'POST',
        url: '{% url "users:add-to-cart" %}',
        data: {
            product_id: product_id,
            product_qty: product_qty,
            csrfmiddlewaretoken: '{{ csrf_token }}',
            action: 'post'
        },
        success: function(response) {
            console.log(response);
            document.getElementById('lblCartCount').textContent = response.qty;
            const add_button = $('.add-button[value="' + product_id + '"]');
            add_button.prop('disabled', true).text("Добавлен").removeClass('btn-info').addClass('btn-success');
        },
        error: function(xhr, status, error) {
            console.log("Ошибка:", xhr.responseText);
            console.log("Статус:", status);
            console.log("Ошибка:", error);
        }
    });
});



const date = new Date();
document.querySelector(".year").innerHTML = date.getFullYear();

setTimeout(function () {
  $("#message").fadeOut("slow");
}, 3000);




// $(document).on('click', '.delete-button', function(e){
//     e.preventDefault();
//     $.ajax({
//       type: 'POST',
//       url: "{% url 'users:delete-to-cart' %}",
//       data:{
//         product_id: $(this).data('index'),
//         csrfmiddlewaretoken: '{{csrf_token}}',
//         action: 'post'
//       },
//       success: function(response){
//         document.getElementById('lblCartCount').textContent = response.qty
//         document.getElementById('total').textContent = response.total
  
//         location.reload()
//       },
//       error: function(error, status){
//         console.log(error, status)
//       }
//     })
//   })
  
  
  
//   $(document).on('click', '.update-button', function(e){
//     e.preventDefault();
  
//     var product_id = $(this).data('index')
//     $.ajax({
//       type: 'POST',
//       url: "{% url 'users:update-to-cart' %}",
//       data:{
//         product_id: $(this).data('index'),
//         product_qty: $('#select' +product_id+ ' option:selected').text(),
//         csrfmiddlewaretoken: '{{csrf_token}}',
//         action: 'post'
//       },
//       success: function(response){
//         document.getElementById('lblCartCount').textContent = response.qty
//         document.getElementById('total').textContent = response.total
  
//         location.reload()
//       },
//       error: function(error, status){
//         console.log(error, status)
//       }
//     })
//   })
  
  
  