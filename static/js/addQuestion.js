async function populateSelectOptions(selectId, endpoint) {
    const response = await fetch(endpoint);
    const data = await response.json();
    const select = document.getElementById(selectId);
    data.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option.value;
        opt.text = option.text;
        select.add(opt);
    });
}

// Заполнение выпадающих списков
populateSelectOptions('theme', '/get-themes');
populateSelectOptions('direction', '/get-directions');
populateSelectOptions('discipline', '/get-disciplines');

function addQuestion() {
const questionBlock = document.createElement('div');
questionBlock.classList.add('question-block');

questionBlock.innerHTML = `
<label>Тип вопроса</label>
<select name="questionType" onchange="toggleQuestionType(this)">
    <option value="с единственным выбором ответа">с единственным выбором ответа</option>
    <option value="с множественным выбором ответа">с множественным выбором ответа</option>
    <option value="с вводом значения">с вводом значения</option>
</select>

<label>Вопрос</label>
<textarea name="question" placeholder="Введите вопрос" required></textarea>

<div class="answer-options" style="display: none;">
    <label>Варианты ответов</label>
    <button type="button" class="add-option-button" onclick="addOption(this)">Добавить вариант ответа</button>
    <div id="answer-options-container"></div>
</div>

<div class="correct-answer" style="display: none;">
    <label>Правильный ответ</label>
    <textarea name="correct-answer" placeholder="Введите правильный ответ" required></textarea>
</div>

<label for="score">Максимальный балл</label>
<input type="number" name="score" min="1" max="10" required>
`;

document.getElementById('questions-container').appendChild(questionBlock);
}


function toggleQuestionType(select) {
    const questionBlock = select.closest('.question-block');
    const answerOptionsDiv = questionBlock.querySelector('.answer-options');
    const correctAnswerDiv = questionBlock.querySelector('.correct-answer');
    const questionType = select.value;
    const answerOptionsContainer = questionBlock.querySelector('#answer-options-container');

    if (questionType === 'с множественным выбором ответа' || questionType === 'с единственным выбором ответа') {
        answerOptionsDiv.style.display = 'block';
        correctAnswerDiv.style.display = 'none';
        answerOptionsContainer.innerHTML = ''; // Clear previous options
    } else if (questionType === 'с вводом значения') {
        answerOptionsDiv.style.display = 'none';
        correctAnswerDiv.style.display = 'block';
    } else {
        answerOptionsDiv.style.display = 'none';
        correctAnswerDiv.style.display = 'none';
    }
}

function addOption(button) {
    const questionBlock = button.closest('.question-block');
    const answerOptionsContainer = questionBlock.querySelector('#answer-options-container');
    const questionTypeSelect = questionBlock.querySelector('select');
    const questionType = questionTypeSelect.value;
    const optionCount = answerOptionsContainer.querySelectorAll('textarea').length + 1;

    const newOption = document.createElement('div');
    newOption.classList.add('option-container');
    const inputType = questionType === 'с единственным выбором ответа' ? 'radio' : 'checkbox';
    newOption.innerHTML = `
        <input type="${inputType}" name="correct-answer-${optionCount}">
        <textarea name="option-${optionCount}" placeholder="Введите вариант ответа ${optionCount}" required></textarea>`;

    const addButton = answerOptionsContainer.querySelector('button');
    answerOptionsContainer.insertBefore(newOption, addButton);
}

async function submitForm(event) {
    event.preventDefault();
    console.log('Функция submitForm вызвана');

    const form = document.getElementById('test-form');
    const formData = new FormData(form);

    // Вывод данных формы в консоль
    for (let pair of formData.entries()) {
        console.log(pair[0] + ', ' + pair[1]);
    }

    const response = await fetch('/create-question', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    if (result.status === 'success') {
        alert('Вопрос создан успешно!');
    } else {
        alert('Не удалось создать вопрос.');
    }
}

// Вызов функции addQuestion при загрузке страницы
window.addEventListener('load', addQuestion);
document.getElementById('test-form').addEventListener('submit', submitForm);