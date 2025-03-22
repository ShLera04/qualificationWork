async function populateSelectOptions(selectId, endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const select = document.getElementById(selectId);
        data.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.text = option.text;
            select.add(opt);
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Заполнение выпадающих списков
populateSelectOptions('theme', '/get-themes');
populateSelectOptions('direction', '/get-directions');
populateSelectOptions('discipline', '/get-disciplines');

// Функция для отправки формы
async function submitForm() {
    const form = document.getElementById('testForm');
    const formData = new FormData(form);

    const response = await fetch('/create-test', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.status === 'success') {
        alert('Тест создан успешно!');
    } else {
        alert('Не удалось создать тест.');
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