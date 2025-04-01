const modal = document.getElementById('modal');
const openModalButton = document.getElementById('bottone1');
const closeModalButton = document.getElementById('closeModal');
const addTopicButton = document.getElementById('addTopicButton');
const topicInput = document.getElementById('topicInput');

const adminModal = document.getElementById('adminModal');
const openAdminModalButton = document.getElementById('bottone2');
const closeAdminModalButton = document.getElementById('closeAdminModal');
const addAdminButton = document.getElementById('addAdminButton');
const adminInput = document.getElementById('adminInput');

const cardsContainer = document.getElementById('cardsContainer');
const burgerMenu = document.getElementById('burgerMenu');
const menuOverlay = document.getElementById('menuOverlay');
const closeMenu = document.getElementById('closeMenu');

// Обновление кнопок прокрутки
function updateButtons() {
    const container = document.querySelector('.cards-container');
    const leftButton = document.querySelector('.scroll-button.left');
    const rightButton = document.querySelector('.scroll-button.right');

    leftButton.disabled = container.scrollLeft === 0;
    rightButton.disabled = container.scrollLeft + container.clientWidth >= container.scrollWidth;
}

function scrollLeft() {
    const container = document.querySelector('.cards-container');
    if (container.scrollLeft > 0) {
        container.scrollBy({
            left: -350,
            behavior: 'smooth'
        });
    }
}

function scrollRight() {
    const container = document.querySelector('.cards-container');
    if (container.scrollLeft + container.clientWidth < container.scrollWidth) {
        container.scrollBy({
            left: 350,
            behavior: 'smooth'
        });
    }
}

// Инициализация состояния кнопок при загрузке
updateButtons();
document.querySelector('.cards-container').addEventListener('scroll', updateButtons);
    function generateButtons(containerId, rows, cols) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const button = document.createElement('button');
            button.className = 'prediction-button';
            button.textContent = `(${i}, ${j})`;
            button.dataset.value = `(${i}, ${j})`;
            button.addEventListener('click', function() {
                button.classList.toggle('selected');
            });
            container.appendChild(button);
        }
    }
}
document.getElementById('generateMatrix').addEventListener('click', function() {
    const rows = parseInt(document.getElementById('rows').value);
    const cols = parseInt(document.getElementById('cols').value);
    const autoFill = document.getElementById('autoFill').checked;
    const matrixContainer = document.getElementById('matrixContainer');
    const matrixContainer2 = document.getElementById('matrixContainer2');
    matrixContainer.innerHTML = '';
    matrixContainer2.innerHTML = '';

    function generateMatrix(container, rows, cols, autoFill, minValue, maxValue) {
        const table = document.createElement('table');
        table.className = 'matrix';
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < cols; j++) {
                const cell = document.createElement('td');
                const input = document.createElement('input');
                input.type = 'number';
                input.style.width = '100%';
                input.style.height = '100%';
                input.style.border = '1px solid #ccc';
                input.style.borderRadius = '4px';
                input.style.fontFamily = 'Roboto, sans-serif';
                input.style.textAlign = 'center';
                input.style.backgroundColor = 'white';
                if (autoFill) {
                    input.value = getRandomValue(minValue, maxValue);
                }
                cell.appendChild(input);
                row.appendChild(cell);
            }
            table.appendChild(row);
        }
        container.appendChild(table);
    }

    function getRandomValue(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    const minValue = autoFill ? parseInt(document.getElementById('minValue').value) : 0;
    const maxValue = autoFill ? parseInt(document.getElementById('maxValue').value) : 0;

    generateMatrix(matrixContainer, rows, cols, autoFill, minValue, maxValue);
    generateMatrix(matrixContainer2, rows, cols, autoFill, minValue, maxValue);

    generateButtons('saddlePointsPrediction1', rows, cols);
    generateButtons('saddlePointsPrediction2', rows, cols);
    generateButtons('nashEquilibriumPrediction', rows, cols);
    generateButtons('paretoOptimalPrediction', rows, cols);
});

document.getElementById('noSaddlePoints1').addEventListener('click', function() {
    this.classList.toggle('selected');
});

document.getElementById('noSaddlePoints2').addEventListener('click', function() {
    this.classList.toggle('selected');
});

document.getElementById('noNashEquilibrium').addEventListener('click', function() {
    this.classList.toggle('selected');
});

document.getElementById('noParetoOptimal').addEventListener('click', function() {
    this.classList.toggle('selected');
});


function getMatrix(containerId) {
    const rows = parseInt(document.getElementById('rows').value);
    const cols = parseInt(document.getElementById('cols').value);
    const matrixContainer = document.getElementById(containerId);
    const matrix = [];

    for (let i = 0; i < rows; i++) {
        const row = [];
        for (let j = 0; j < cols; j++) {
            const input = matrixContainer.querySelectorAll('input')[i * cols + j];
            row.push(parseInt(input.value));
        }
        matrix.push(row);
    }

    return matrix;
}

// function displayResult(result, title) {
//     const resultsContainer = document.getElementById('results');
//     resultsContainer.innerHTML = `<h3>${title}</h3>`;
//     if (result.length > 0) {
//         result.forEach(point => {
//             resultsContainer.innerHTML += `(${point[0]}, ${point[1]})<br>`;
//         });
//     } else {
//         if (title === 'Седловые точки') {
//             resultsContainer.innerHTML += 'Седловые точки не найдены.<br>';
//         } else if (title === 'Равновесие по Нэшу') {
//             resultsContainer.innerHTML += 'Равновесие по Нэшу не найдено.<br>';
//         } else if (title === 'Оптимальность по Парето') {
//             resultsContainer.innerHTML += 'Парето-оптимальные точки не найдены.<br>';
//         }
//     }
// }

function displayResult(result, title) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML += `<h3>${title}</h3>`;
    
    if (result && result.length > 0) {
        result.forEach(point => {
            const i = Array.isArray(point) ? point[0] : point[0];
            const j = Array.isArray(point) ? point[1] : point[1];
            resultsContainer.innerHTML += `(${i}, ${j})<br>`;
        });
    } else {
        resultsContainer.innerHTML += 'Не найдено<br>';
    }
}

function compareResults(prediction, result, title) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML += `<h3>Сравнение предположительных и фактических результатов</h3>`;

    if (prediction.length === 0) {
        resultsContainer.innerHTML += "Предположительные результаты не указаны.<br>";
    } else {
        const predictedPoints = prediction.map(point => 
            point.trim().replace(/[()]/g, '').split(',').map(Number)
        );
        const actualPoints = result.map(point => [point[0], point[1]]);

        const noOption = prediction.includes("НЕТ");
        const actualNoResult = result.length === 0;

        if (noOption && actualNoResult) {
            resultsContainer.innerHTML += "Все предположительные результаты совпадают с фактическими.<br>";
        } else if (noOption || actualNoResult) {
            resultsContainer.innerHTML += "Предположительные результаты не совпадают с фактическими.<br>";
        } else {
            const matchedPoints = predictedPoints.filter(point =>
                actualPoints.some(actualPoint => 
                    actualPoint[0] === point[0] && actualPoint[1] === point[1]
                )
            );

            if (matchedPoints.length === actualPoints.length && matchedPoints.length === predictedPoints.length) {
                resultsContainer.innerHTML += "Все предположительные результаты совпадают с фактическими.<br>";
            } else if (matchedPoints.length > 0) {
                resultsContainer.innerHTML += "Некоторые предположительные результаты совпадают с фактическими: " + 
                    matchedPoints.map(point => `(${point[0]}, ${point[1]})`).join(', ') + "<br>";
            } else {
                resultsContainer.innerHTML += "Предположительные результаты не совпадают с фактическими.<br>";
            }
        }
    }
}

function sendRequest(url, data, prediction, title) {
    if (prediction.length === 0) {
        alert('Предположительные результаты не указаны. Пожалуйста, укажите хотя бы один вариант ответа.');
        return;
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        // Специальная обработка для седловых точек
        if (url === '/saddle_points') {
            // Обрабатываем результаты для обеих матриц
            const results1 = result.matrix_a || [];
            const results2 = result.matrix_b || [];
            
            // Выводим результаты для первой матрицы
            displayResult(results1, 'Седловые точки первой матрицы');
            compareResults(prediction.prediction1, results1, 'Седловые точки первой матрицы');
            
            // Выводим результаты для второй матрицы
            displayResult(results2, 'Седловые точки второй матрицы');
            compareResults(prediction.prediction2, results2, 'Седловые точки второй матрицы');
        } else {
            // Стандартная обработка для других запросов
            const formattedResult = result.map(point => [point[0], point[1]]);
            displayResult(formattedResult, title);
            compareResults(prediction, formattedResult, title);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('results').innerHTML += `<p style="color: red;">Ошибка: ${error.message}</p>`;
    });
}


document.getElementById('optionSelect').addEventListener('change', function() {
    const selectedOption = this.value;
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; 
    if (selectedOption === 'saddlePoints') {
        const matrix1 = getMatrix('matrixContainer');
        const matrix2 = getMatrix('matrixContainer2');
        
        const prediction1 = Array.from(document.querySelectorAll('#saddlePointsPrediction1 .prediction-button.selected')).map(button => button.dataset.value);
        const noSaddlePoints1 = document.getElementById('noSaddlePoints1').classList.contains('selected');
        
        const prediction2 = Array.from(document.querySelectorAll('#saddlePointsPrediction2 .prediction-button.selected')).map(button => button.dataset.value);
        const noSaddlePoints2 = document.getElementById('noSaddlePoints2').classList.contains('selected');

        if (noSaddlePoints1) {
            prediction1.push("НЕТ");
        }
        if (noSaddlePoints2) {
            prediction2.push("НЕТ");
        }

        // Проверяем, что пользователь сделал предварительные предположения для обеих матриц
        if (prediction1.length === 0 || prediction2.length === 0) {
            alert('Пожалуйста, укажите предположительные седловые точки для обеих матриц перед выполнением проверки.');
            return;
        }

        // Проверяем первую матрицу
        sendRequest('/saddle_points', { 
            matrix_a: matrix1, 
            matrix_b: matrix2 
        }, {
            prediction1: prediction1,
            prediction2: prediction2
        }, 'Седловые точки');
    } else if (selectedOption === 'nashEquilibrium') {
        const matrix_a = getMatrix('matrixContainer');
        const matrix_b = getMatrix('matrixContainer2');
        const prediction = Array.from(document.querySelectorAll('#nashEquilibriumPrediction .prediction-button.selected')).map(button => button.dataset.value);
        const noNashEquilibrium = document.getElementById('noNashEquilibrium').classList.contains('selected');

        if (noNashEquilibrium) {
            prediction.push("НЕТ");
        }

        sendRequest('/nash_equilibrium', { matrix_a: matrix_a, matrix_b: matrix_b }, prediction, 'Равновесие по Нэшу');
    } else if (selectedOption === 'paretoOptimal') {
        const matrix_a = getMatrix('matrixContainer');
        const matrix_b = getMatrix('matrixContainer2');
        const prediction = Array.from(document.querySelectorAll('#paretoOptimalPrediction .prediction-button.selected')).map(button => button.dataset.value);
        const noParetoOptimal = document.getElementById('noParetoOptimal').classList.contains('selected');

        if (noParetoOptimal) {
            prediction.push("НЕТ");
        }

        sendRequest('/pareto_optimal', { matrix_a: matrix_a, matrix_b: matrix_b }, prediction, 'Оптимальность по Парето');
    }
});

// Загрузка тем из базы данных и отображение их в карточках
document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-themes')
        .then(response => response.json())
        .then(themes => {
            const cardsContainer = document.getElementById('cardsContainer');
            themes.forEach((theme, index) => {
                const card = document.createElement('div');
                card.className = 'cards';
                card.innerHTML = `
                    <p>Раздел №${index + 1}</p>
                    <p>Тема:</p>
                    <a href="../page${index + 1}">
                        <p>"${theme.name}"</p>
                    </a>
                `;
                cardsContainer.appendChild(card);
            });
            updateButtons();
        })
        .catch(error => console.error('Error:', error));
});

burgerMenu.addEventListener('click', () => {
    menuOverlay.classList.toggle('active');
});

closeMenu.addEventListener('click', () => {
    menuOverlay.classList.remove('active');
});

// Закрытие бургер-меню при клике вне его
menuOverlay.addEventListener('click', (event) => {
    if (event.target === menuOverlay) {
        menuOverlay.classList.remove('active');
     }
});

// Закрытие бургер-меню при выборе пункта меню
const menuItems = document.querySelectorAll('.menu-item');
menuItems.forEach(item => {
     item.addEventListener('click', () => {
        menuOverlay.classList.remove('active');
    });
});

document.getElementById('inputSearchSecond').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const cards = document.querySelectorAll('.cards');

    cards.forEach(card => {
        const themeName = card.querySelector('a p').textContent.toLowerCase();
        if (themeName.includes(query)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});