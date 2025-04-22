async function populateSelectOptions(selectId, endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Ошибка сети');
        const data = await response.json();
        
        const select = document.getElementById(selectId);
        data.forEach(item => {
            const opt = document.createElement('option');
            // Используем поле 'name' из серверного ответа
            opt.value = item.name;  // Если нужно ID, потребуется изменение на сервере
            opt.textContent = item.name; // Отображаемое имя
            select.appendChild(opt);
        });
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    populateSelectOptions('theme', '/get-themes');
    populateSelectOptions('direction', '/get-directions');
});
// Функция для отправки формы
async function submitForm() {
    try {
        const response = await fetch('/create-test', {
            method: 'POST',
            body: new FormData(document.getElementById('testForm'))
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Неизвестная ошибка');
        }

        // Успешное выполнение
        showFlashMessage(data.message, 'success');
        resetForm();

    } catch (error) {
        // Обработка ошибок
        showFlashMessage(error.message, 'error');
    }
}
// Функция для валидации ввода чисел
function validateNumber(input) {
    if (input.value < 0) {
        input.value = 0;
    }
}

// Функция для обновления общего количества вопросов
function updateTotalQuestions() {
    const easyQuestions = parseInt(document.getElementById('easyQuestions').value) || 0;
    const mediumQuestions = parseInt(document.getElementById('mediumQuestions').value) || 0;
    const hardQuestions = parseInt(document.getElementById('hardQuestions').value) || 0;
    const totalQuestions = easyQuestions + mediumQuestions + hardQuestions;
    document.getElementById('totalQuestions').value = totalQuestions;
}

// Функция для обновления сложности теста
function updateTestDifficulty() {
    const easyQuestions = parseInt(document.getElementById('easyQuestions').value) || 0;
    const mediumQuestions = parseInt(document.getElementById('mediumQuestions').value) || 0;
    const hardQuestions = parseInt(document.getElementById('hardQuestions').value) || 0;
    const totalQuestions = easyQuestions + mediumQuestions + hardQuestions;

    if (totalQuestions === 0) {
        document.getElementById('testDifficulty').value = 'Не определена';
        return;
    }

    const easyWeight = 1;
    const mediumWeight = 2;
    const hardWeight = 3;
    const maxDifficulty = 3 * totalQuestions;
    const difficulty = (easyWeight * easyQuestions) + (mediumWeight * mediumQuestions) + (hardWeight * hardQuestions);
    const difficultyPercentage = (difficulty / maxDifficulty) * 100;

    let difficultyLevel;
    if (difficultyPercentage <= 60) {
        difficultyLevel = 'легкий';
    } else if (difficultyPercentage <= 75) {
        difficultyLevel = 'средний';
    } else {
        difficultyLevel = 'сложный';
    }

    document.getElementById('testDifficulty').value = difficultyLevel;
}

// Добавьте эти функции в createTest.js
function showFlashMessage(message, type) {
    const flashesContainer = document.querySelector('.flashes');
    flashesContainer.innerHTML = '';
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    flashesContainer.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

function resetForm() {
    document.getElementById('testForm').reset();
    document.getElementById('totalQuestions').value = '';
    document.getElementById('testDifficulty').value = '';
}
