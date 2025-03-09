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


const date = new Date();
document.querySelector(".year").innerHTML = date.getFullYear();

setTimeout(function () {
  $("#message").fadeOut("slow");
}, 3000);



  


  
  