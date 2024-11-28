// Убедитесь, что Telegram Web App API загружен
window.Telegram.WebApp.ready();

// Функция для проверки состояния активности
function checkIsActive() {
    const isActive = Telegram.WebApp.isActive; // Получаем значение isActive
    return isActive;
}

// Пример использования в обработчике события visibilitychange
document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === "visible" && checkIsActive()) {
        // Программно перезагружаем форму или нужные поля
        document.getElementById('export-form').reset();
    }
});

const searchInput = document.getElementById("search-input");  // Для поля с фирмой
const addressInput = document.getElementById("address-input");  // Для поля с адресом
const suggestionsContainer = document.getElementById("suggestions-container");
const addresssuggestionsContainer = document.getElementById("address-suggestions");

console.log(document.visibilityState);

// Обработчик для поля "search" (фирма)
searchInput.addEventListener("input", async function () {
    const query = this.value;

    if (query.length >= 2) {
        try {
            // Запрос на поиск фирмы
            const response = await fetch(`/search_firm?query=${query}`);

            // Проверка на успешность запроса
            if (!response.ok) {
                console.error("Ошибка запроса:", response.status);
                return;
            }

            const suggestions = await response.json();

            // Проверяем, что suggestions — массив, перед тем как выполнять forEach
            if (!Array.isArray(suggestions)) {
                console.error("Неверный формат данных, ожидался массив:", suggestions);
                return;
            }

            suggestionsContainer.innerHTML = "";
            suggestions.forEach(suggestion => {
                const item = document.createElement("div");
                item.classList.add("suggestion-item");
                item.textContent = suggestion;
                item.onclick = function () {
                    searchInput.value = suggestion;
                    suggestionsContainer.innerHTML = "";
                    suggestionsContainer.style.display = "none";
                };
                suggestionsContainer.appendChild(item);
            });

            suggestionsContainer.style.display = suggestions.length ? "block" : "none";
        } catch (error) {
            console.error("Ошибка при выполнении запроса:", error);
        }
    } else {
        suggestionsContainer.innerHTML = "";
        suggestionsContainer.style.display = "none";
    }
});

// Обработчик для поля "address"
addressInput.addEventListener("input", async function () {
    const query = this.value;  // Это то, что вводит пользователь в поле для адреса
    const firmQuery = searchInput.value;  // Это то, что было введено в поле для фирмы

    if (query.length >= 1 && firmQuery.length > 0) {
        try {
            // Запрос для поиска адресов по firmQuery (значение из поля "search") и query (значение из поля "address")
            const response = await fetch(`/search_address?query=${query}&firm=${firmQuery}`);

            // Проверка на успешность запроса
            if (!response.ok) {
                console.error("Ошибка запроса:", response.status);
                return;
            }

            const suggestions = await response.json();
            console.log(suggestions)
            // Проверяем, что suggestions — массив, перед тем как выполнять forEach
            if (!Array.isArray(suggestions)) {
                console.error("Неверный формат данных, ожидался массив:", suggestions);
                return;
            }

            addresssuggestionsContainer.innerHTML = "";

            suggestions.forEach(suggestion => {
                const item = document.createElement("div");
                item.classList.add("suggestion-item");
                item.textContent = suggestion;
                item.onclick = function () {
                    addressInput.value = suggestion;
                    addresssuggestionsContainer.innerHTML = "";
                    addresssuggestionsContainer.style.display = "none";
                };
                addresssuggestionsContainer.appendChild(item);
            });

            addresssuggestionsContainer.style.display = suggestions.length ? "block" : "none";
        } catch (error) {
            console.error("Ошибка при выполнении запроса:", error);
        }
    } else {
        addresssuggestionsContainer.innerHTML = "";
        addresssuggestionsContainer.style.display = "none";
    }
});


    // Обработчик для поля выбора
const choiceField = document.getElementById("choice");
const weightField = document.getElementById("weight-field");
const weightInput = document.getElementById("weight");

// Функция для отображения или скрытия поля веса в зависимости от выбора
function toggleWeightField() {
    if (choiceField.value === "вектор") {
        weightField.style.display = "block";  // Показываем поле для веса
        weightInput.required = true;         // Делаем поле обязательным
    } else {
        weightField.style.display = "none";   // Скрываем поле для веса
        weightInput.required = false;        // Убираем обязательность
    }
}

// Инициализация состояния при загрузке
toggleWeightField();

// Добавляем обработчик события
choiceField.addEventListener("change", toggleWeightField);

// Обработчик для изменения значения в селекте "action"
document.getElementById('action').addEventListener('change', function() {
    var takenBasketField = document.getElementById('taken_basket_number');
    var placedBasketField = document.getElementById('placed_basket_number');
    var takenBasketLabel = document.querySelector('label[for="taken_basket_number"]');
    var placedBasketLabel = document.querySelector('label[for="placed_basket_number"]');
    var choiceField = document.getElementById('choice');
    var choiceLabel = document.querySelector('label[for="choice"]');

    // Если выбран вариант "Выставил", скрываем поле "Номер взятого бака" и его лейбл
    if (this.value === 'выставил') {
        takenBasketField.style.display = 'none';  // Скрываем поле "Номер взятого бака"
        takenBasketLabel.style.display = 'none';  // Скрываем лейбл "Номер взятого бака"
        placedBasketField.style.display = 'block';  // Показываем поле "Номер выстав. бака"
        placedBasketLabel.style.display = 'block';  // Показываем лейбл "Номер поставленного бака"
        choiceField.style.display = 'none';
        choiceField.removeAttribute('required');
        choiceLabel.style.display = 'none';
        weightField.style.display = "none";   // Скрываем поле для веса
        weightInput.required = false;        // Убираем обязательность

        // Удаляем значение из поля choice перед отправкой
        choiceField.value = '';  // Очищаем значение

    }
    // Если выбран вариант "Забрал", скрываем поле "Номер поставленного бака" и его лейбл
    else if (this.value === 'забрал') {
        takenBasketField.style.display = 'block';  // Показываем поле "Номер взятого бака"
        takenBasketLabel.style.display = 'block';  // Показываем лейбл "Номер взятого бака"
        placedBasketField.style.display = 'none';  // Скрываем поле "Номер поставленного бака"
        placedBasketLabel.style.display = 'none';  // Скрываем лейбл "Номер поставленного бака"
        choiceField.style.display = 'block';
        choiceLabel.style.display = 'block';

    } else {
        // В случае других значений (если нужно вернуть по умолчанию)
        takenBasketField.style.display = 'block';  // Показываем оба поля
        takenBasketLabel.style.display = 'block';  // Показываем лейбл "Номер взятого бака"
        placedBasketField.style.display = 'block';  // Показываем оба поля
        placedBasketLabel.style.display = 'block';  // Показываем лейбл "Номер поставленного бака"
        choiceField.style.display = 'block';
        choiceLabel.style.display = 'block';

    }
});

// Скрывать список предложений при потере фокуса
searchInput.addEventListener("blur", function () {
    setTimeout(() => {
        suggestionsContainer.style.display = "none";
    }, 200); // Небольшая задержка, чтобы успеть кликнуть по предложению
});

// Скрывать список предложений при потере фокуса
addressInput.addEventListener("blur", function () {
    setTimeout(() => {
        addresssuggestionsContainer.style.display = "none";
    }, 200); // Небольшая задержка, чтобы успеть кликнуть по предложению
});

// Закрытие списка предложений, если кликнули вне поля ввода и списка
document.addEventListener("click", function(event) {
    if (!searchInput.contains(event.target) && !suggestionsContainer.contains(event.target)) {
        suggestionsContainer.style.display = "none";
    }
});

// Функция скрытия уведомления
function hideNotification() {
    const notification = document.getElementById("notification");
    notification.style.opacity = "0";
    setTimeout(() => notification.style.display = "none", 500); // Ждем окончания анимации
}

// Автоматическое скрытие уведомления через 3 секунды
setTimeout(hideNotification, 3000);

// // Функция для восстановления фокуса на первом input
// function restoreFocus() {
//     const inputFields = document.querySelectorAll('input');
    
//     // Восстановить фокус на первом поле ввода
//     if (inputFields.length > 0) {
//         inputFields[0].focus();
//     }
// }

// // Обработчик события visibilitychange
// document.addEventListener("visibilitychange", function() {
//     // Проверяем, если страница снова видима
//     if (document.visibilityState === "visible") {
//         restoreFocus();
//     }
// });
