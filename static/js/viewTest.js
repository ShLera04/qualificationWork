const initialQuestions = window.initialQuestions;
const test_name = window.test_name;

let currentQuestion = 0;
let answers = {}; 
let questions = initialQuestions;
let testAttempts = [];

async function loadAttempts() {
    try {
        const response = await fetch(`/get-attempts/${test_name}`);
        const data = await response.json();

        if (data.success) {
            testAttempts = data.attempts;
            renderAttempts();
        } else {
            console.error('Ошибка загрузки попыток:', data.error);
            document.getElementById('attemptsList').innerHTML = '<p>Ошибка загрузки информации о попытках</p>';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('attemptsList').innerHTML = '<p>Ошибка загрузки информации о попытках</p>';
    }
}


function renderAttempts() {
    const attemptsList = document.getElementById('attemptsList');

    if (!testAttempts || testAttempts.length === 0) {
        attemptsList.innerHTML = '<p>Вы еще не проходили этот тест</p>';
        return;
    }

    let html = '<h3>Ваши предыдущие попытки:</h3>';

    testAttempts.forEach(attempt => {
        const date = new Date(attempt.attempt_data);
        const formattedDate = date.toLocaleString('ru-RU');

        html += `
            <div class="attempt-item">
                <p><strong>Дата прохождения:</strong> ${formattedDate}</p>
                <p><strong>Итоговая оценка:</strong> ${attempt.mark}</p>
            </div>
        `;
    });

    attemptsList.innerHTML = html;
}

function startTest() {
    document.getElementById('attemptsContainer').style.display = 'none';
    document.getElementById('mainTestContainer').style.display = 'block';

    if (!questions || questions.length === 0) {
        showEmptyTestMessage();
        return;
    }

    renderQuestionNavigation();
    showQuestion(currentQuestion);
    updateProgress();
    setupEventListeners();
}

document.addEventListener('DOMContentLoaded', () => {
    loadAttempts();

    document.getElementById('startTestBtn').addEventListener('click', startTest);
});
function showQuestion(index) {
const question = questions[index];

document.getElementById('questionNumber').textContent = `Вопрос ${index + 1}`;
document.getElementById('questionText').textContent = question.question_text;

const imageContainer = document.getElementById('imageContainer');
const imgElement = document.getElementById('questionImage');

if (question.image) {
    imgElement.src = `data:image/jpeg;base64,${question.image}`;
    imageContainer.style.display = 'block';
} else {
    imageContainer.style.display = 'none';
}

const optionsContainer = document.getElementById('optionsContainer');
const inputField = document.getElementById('inputField');
optionsContainer.innerHTML = '';
inputField.style.display = 'none';

if (question.question_type === 'с вводом значения') {
    inputField.style.display = 'block';
    inputField.value = answers[index] || '';
} else if (question.question_type === 'с единственным выбором ответа') {
    question.answers.forEach(option => {
        const optionElement = document.createElement('div');
        optionElement.className = 'option-item';
        
        const isChecked = String(answers[index]) === String(option.answer_id);
        
        optionElement.innerHTML = `
            <label class="option-label">
                <input type="radio" name="answer" class="option-input"
                        value="${option.answer_id}" ${isChecked ? 'checked' : ''}>
                ${option.answer_text}
            </label>
        `;
        optionsContainer.appendChild(optionElement);
    });
}

document.querySelectorAll('.question-link').forEach(link => {
    link.classList.remove('current');
});
document.querySelectorAll('.question-link')[index].classList.add('current');
}

function setupEventListeners() {
    document.getElementById('prevQuestion').addEventListener('click', () => {
        saveCurrentAnswer(); 
        if (currentQuestion > 0) {
            currentQuestion--;
            showQuestion(currentQuestion);
        }
    });

    document.getElementById('nextQuestion').addEventListener('click', () => {
        saveCurrentAnswer();
        if (currentQuestion < questions.length - 1) {
            currentQuestion++;
            showQuestion(currentQuestion);
        }
    });

    document.getElementById('optionsContainer').addEventListener('change', (e) => {
        if (e.target.name === 'answer') {
            answers[currentQuestion] = e.target.value;
            updateProgress();
            renderQuestionNavigation();
        }
    });

    document.getElementById('inputField').addEventListener('input', (e) => {
        answers[currentQuestion] = e.target.value;
        updateProgress();
        renderQuestionNavigation();
    });

    document.getElementById('submitTest').addEventListener('click', submitTest);
}

function saveCurrentAnswer() {
    const question = questions[currentQuestion];
    let hasAnswer = false;
    
    if (question.question_type === 'с вводом значения') {
        const inputValue = document.getElementById('inputField').value.trim();
        if (inputValue !== '') {
            answers[currentQuestion] = inputValue;
            hasAnswer = true;
        } else {
            delete answers[currentQuestion];
        }
    } else if (question.question_type === 'с единственным выбором ответа') {
        const selectedOption = document.querySelector('input[name="answer"]:checked');
        if (selectedOption) {
            answers[currentQuestion] = String(selectedOption.value);
            hasAnswer = true;
        } else {
            delete answers[currentQuestion];
        }
    }
    
    if (hasAnswer) {
        updateProgress();
        renderQuestionNavigation();
    }
}
function renderQuestionNavigation() {
    const navContainer = document.getElementById('questionNav');
    navContainer.innerHTML = '';

    questions.forEach((q, index) => {
        const link = document.createElement('div');
        link.className = `question-link ${index === currentQuestion ? 'current' : ''} ${answers[index] ? 'answered' : ''}`;
        link.textContent = index + 1;
        link.onclick = () => {
            saveCurrentAnswer();
            currentQuestion = index;
            showQuestion(index);
        };
        navContainer.appendChild(link);
    });
}

function updateProgress() {
    const answered = Object.keys(answers).filter(key =>
        answers[key] !== undefined && answers[key] !== ''
    ).length;

    const progress = (answered / questions.length) * 100;
    document.getElementById('progress').style.width = `${progress}%`;
}

function showResults(correctAnswers, totalQuestions, mark) {
    document.querySelector('.container').innerHTML = `
        <div class="results-container">
            <h2 class="results-title">Тест завершен!</h2>
            <div class="results-text">
                <p>Вы ответили правильно на <strong>${correctAnswers} из ${totalQuestions}</strong> вопросов</p>
                <p>Ваша оценка: <strong>${mark}</strong></p>
            </div>
            <button class="home-button" id="goHome">Вернуться на главную</button>
        </div>
    `;
    
    document.getElementById('goHome').addEventListener('click', () => {
        window.location.href = '/mainStudent'; 
    });
}


async function submitTest() {
    saveCurrentAnswer();
    
    let correctAnswers = 0;
    let totalScore = 0;
    let userScore = 0;
    
    questions.forEach((question, index) => {
        const userAnswer = answers[index];
        totalScore += question.max_score || 1;

        if (question.question_type === 'с вводом значения') {
            const correctAnswer = question.answers.find(a => a.is_correct)?.answer_text;
            if (String(userAnswer).trim() === String(correctAnswer).trim()) {
                correctAnswers++;
                userScore += question.max_score || 1;
            }
        } else if (question.question_type === 'с единственным выбором ответа') {
            const correctAnswerId = question.answers.find(a => a.is_correct)?.answer_id;
            if (userAnswer == correctAnswerId) {
                correctAnswers++;
                userScore += question.max_score || 1;
            }
        }
    });

    const percentage = (userScore / totalScore) * 100;
    
    let mark;
    if (percentage >= 90) mark = 5;
    else if (percentage >= 76) mark = 4;
    else if (percentage >= 60) mark = 3;
    else mark = 2;

    try {
        const response = await fetch('/save_attempt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                test_id: JSON.parse('{{ test_id|tojson|safe }}'),
                mark: mark,
                score: userScore,
                total_score: totalScore,
                correct_answers: correctAnswers,
                total_questions: questions.length
            })
        });

        const result = await response.json();
        
        if (result.success) {
            showResults(correctAnswers, questions.length, mark);
        } else {
            showResults(correctAnswers, questions.length, mark);
            console.error('Ошибка сохранения:', result.message);
        }
    } catch (error) {
        showResults(correctAnswers, questions.length, mark);
        console.error('Ошибка:', error);
    }
}

function showEmptyTestMessage() {
    document.querySelector('.container').innerHTML = `
        <div class="results-container">
            <h2 class="results-title">Тест недоступен</h2>
            <div class="results-text">
                <p>Нет доступных вопросов для этого теста.</p>
                <p>Пожалуйста, попробуйте позже.</p>
            </div>
            <button class="home-button" id="goHome">Вернуться на главную</button>
        </div>
    `;
    
    document.getElementById('goHome').addEventListener('click', () => {
        window.location.href = '/mainStudent';
    });
}