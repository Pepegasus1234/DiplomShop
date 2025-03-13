document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('.rating-selector .star');
    const ratingInput = document.getElementById('rating-input');

    stars.forEach(star => {
        star.addEventListener('click', function () {
            const value = this.getAttribute('data-value');

            // Убираем класс selected у всех звезд
            stars.forEach(s => s.classList.remove('selected'));

            // Добавляем класс selected к выбранным звездам
            for (let i = 0; i < value; i++) {
                stars[i].classList.add('selected');
            }

            // Обновляем значение скрытого поля
            ratingInput.value = value;
        });

        star.addEventListener('mouseover', function () {
            const value = this.getAttribute('data-value');
            stars.forEach((s, index) => {
                if (index < value) {
                    s.style.color = '#ffcc00';
                } else {
                    s.style.color = '#ccc';
                }
            });
        });

        star.addEventListener('mouseout', function () {
            stars.forEach(s => {
                s.style.color = s.classList.contains('selected') ? '#ffcc00' : '#ccc';
            });
        });
    });
});