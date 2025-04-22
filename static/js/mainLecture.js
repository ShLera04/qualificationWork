const modal = document.getElementById('modal');
        const cardsContainer = document.getElementById('cardsContainer');
        const burgerMenu = document.getElementById('burgerMenu');
        const menuOverlay = document.getElementById('menuOverlay');
        const closeMenu = document.getElementById('closeMenu');

        fetch('/get_user_info')
        .then(response => response.json())
        .then(data => {
            if(data.logged_in) {
            document.querySelector('.username').textContent = data.login;
            }
        });

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

        function displayResult(result, title) {
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = `<h3>${title}</h3>`;
        
            if (title === 'Седловые точки') {
                // Обработка объекта с двумя массивами
                let hasPoints = false;
                
                if (result.matrix_a && result.matrix_a.length > 0) {
                    resultsContainer.innerHTML += '<h4>Для игрока A:</h4>';
                    result.matrix_a.forEach(point => {
                        resultsContainer.innerHTML += `(${point[0]}, ${point[1]})<br>`;
                    });
                    hasPoints = true;
                }
                
                if (result.matrix_b && result.matrix_b.length > 0) {
                    resultsContainer.innerHTML += '<h4>Для игрока B:</h4>';
                    result.matrix_b.forEach(point => {
                        resultsContainer.innerHTML += `(${point[0]}, ${point[1]})<br>`;
                    });
                    hasPoints = true;
                }
                
                if (!hasPoints) {
                    resultsContainer.innerHTML += 'Седловые точки не найдены.<br>';
                }
            }
            else {
                // Обработка массива для Нэша и Парето
                if (Array.isArray(result) && result.length > 0) {
                    result.forEach(point => {
                        const coords = title === 'Оптимальность по Парето' 
                            ? `${point[0]}, ${point[1]}`
                            : `${point[0]}, ${point[1]}`;
                        
                        resultsContainer.innerHTML += `(${coords})<br>`;
                    });
                } else {
                    const messages = {
                        'Равновесие по Нэшу': 'Равновесие по Нэшу не найдено.<br>',
                        'Оптимальность по Парето': 'Парето-оптимальные точки не найдены.<br>'
                    };
                    resultsContainer.innerHTML += messages[title] || 'Результатов нет.<br>';
                }
            }
        }

        function sendRequest(url, data, title) {
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                // Убираем преобразование через map
                displayResult(result, title);
            })
            .catch(error => console.error('Error:', error));
        }
        
        document.getElementById('optionSelect').addEventListener('change', function() {
            const selectedOption = this.value;
            if (selectedOption === 'saddlePoints') {
                const matrix_a = getMatrix('matrixContainer');
                const matrix_b = getMatrix('matrixContainer2');
                sendRequest('/saddle_points', 
                    { matrix_a: matrix_a, matrix_b: matrix_b }, 
                    'Седловые точки'
                );
            } else if (selectedOption === 'nashEquilibrium') {
                const matrix_a = getMatrix('matrixContainer');
                const matrix_b = getMatrix('matrixContainer2');
                sendRequest('/nash_equilibrium', { matrix_a: matrix_a, matrix_b: matrix_b }, 'Равновесие по Нэшу');
            } else if (selectedOption === 'paretoOptimal') {
                const matrix_a = getMatrix('matrixContainer');
                const matrix_b = getMatrix('matrixContainer2');
                sendRequest('/pareto_optimal', { matrix_a: matrix_a, matrix_b: matrix_b }, 'Оптимальность по Парето');
            }
        });

        // Загрузка тем из базы данных и отображение их в карточках
        document.addEventListener('DOMContentLoaded', function () {
            const cardsContainer = document.getElementById('cardsContainer');
    
            // Загрузка тем из базы данных и отображение их в карточках
            fetch('/get-themes')
                .then(response => response.json())
                .then(themes => {
                    themes.forEach((theme, index) => {
                        const card = document.createElement('a');
                        card.className = 'cards';
                        card.href = `/section/${encodeURIComponent(theme.name)}`;
                        card.innerHTML = `
                            <p>Раздел №${index + 1}</p>
                            <p>Тема:</p>
                            <p>"${theme.name}"</p>
                        `;
                        cardsContainer.appendChild(card);
                    });
                    updateButtons();
                })
                .catch(error => console.error('Error:', error));
        });
        // Открытие и закрытие бургер-меню
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

        document.getElementById('inputSearch').addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const cards = document.querySelectorAll('.cards');
        
            cards.forEach(card => {
                const themeName = card.textContent.toLowerCase();
                if (themeName.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
    // Генератор матриц с седловыми точками
    document.getElementById('generateSaddleMatrix').addEventListener('click', function() {
        const rows = parseInt(document.getElementById('saddleRows').value);
        const cols = parseInt(document.getElementById('saddleCols').value);
        const k = parseInt(document.getElementById('saddlePointsCount').value);
    
        // Очистка контейнера матрицы перед новым запросом
        // Проверка ввода
        if (rows < 1 || cols < 1) {
            showFlashMessage("Все значения должны быть положительными числами", 'error', '#saddleGenerator .second_container');
            return;
        }
    
        const maxPossible = rows * cols;
        if (k > maxPossible) {
            showFlashMessage(`Количество седловых точек не может превышать ${maxPossible}`, 'error', '#saddleGenerator .second_container');
            return;
        }
        if (k < 0) {
            showFlashMessage("Количество седловых точек должно быть неотрицательным числом", 'error', '#saddleGenerator .second_container');
            return;
        }
    
        fetch('/generate_saddle_matrix', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rows: rows,
                cols: cols,
                k: k
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error); });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showFlashMessage(data.error, 'error', '#saddleGenerator .second_container');
                return;
            }
    
            const container = document.getElementById('saddleMatrixContainer');
            container.innerHTML = '';
            container.className = 'matrix-container';
    
            const table = document.createElement('table');
            table.className = 'matrix';
    
            // Создаем заголовок таблицы
            const headerRow = document.createElement('tr');
            headerRow.appendChild(document.createElement('th')); // Пустая ячейка
            for (let j = 0; j < cols; j++) {
                const th = document.createElement('th');
                headerRow.appendChild(th);
            }
            table.appendChild(headerRow);
    
            // Заполняем матрицу
            for (let i = 0; i < rows; i++) {
                const row = document.createElement('tr');
                const rowHeader = document.createElement('th');
                row.appendChild(rowHeader);
    
                for (let j = 0; j < cols; j++) {
                    const cell = document.createElement('td');
                    cell.textContent = data.matrix[i][j];
                    cell.style.color = 'white';
    
                    // Проверяем, является ли седловой точкой
                    const isSaddle = data.saddle_points.some(p => p[0] === i && p[1] === j);
                    if (isSaddle) {
                        cell.style.backgroundColor = 'hsl(205, 51%, 93%)';
                        cell.style.fontWeight = 'bold';
                        cell.style.color = 'black';
                        cell.title = 'Седловая точка';
                    }
    
                    row.appendChild(cell);
                }
                table.appendChild(row);
            }
    
            container.appendChild(table);
    
            // Выводим результаты
            const resultContainer = document.getElementById('saddleMatrixResult');
    
            if (data.saddle_points.length !== k) {
                resultContainer.innerHTML += `
                    <p style="color: red;">
                        Внимание: количество седловых точек не соответствует запросу!
                    </p>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const container = document.getElementById('saddleMatrixContainer');
            container.innerHTML = '';
            container.className = 'matrix-container';

            const resultContainer = document.getElementById('saddleMatrixResult');
            resultContainer.innerHTML = '';
            showFlashMessage(error.message, 'error', '#saddleGenerator .second_container');
        })
        .finally(() => {
            this.disabled = false;
            this.textContent = "Сгенерировать";
        });
    });
    
    
    /**
 * Универсальная функция для отображения flash-сообщений.
 * @param {string} message - Текст сообщения.
 * @param {string} type - Тип сообщения: 'success', 'error', 'warning'.
 * @param {string|HTMLElement} containerSelector - Селектор или элемент контейнера, в котором будет отображаться сообщение.
 */
function showFlashMessage(message, type, containerSelector) {
    let box;
    if (typeof containerSelector === 'string') {
        box = document.querySelector(containerSelector);
    } else if (containerSelector instanceof HTMLElement) {
        box = containerSelector;
    } else {
        console.error('Неверный контейнер:', containerSelector);
        return;
    }

    if (!box) {
        console.error('Контейнер не найден:', containerSelector);
        return;
    }

    let flashesContainer = box.querySelector('.flashes');

    if (!flashesContainer) {
        flashesContainer = document.createElement('div');
        flashesContainer.className = 'flashes';

        const h2Element = box.querySelector('h2.nameSection');
        if (h2Element) {
            h2Element.insertAdjacentElement('afterend', flashesContainer);
        } else {
            box.insertBefore(flashesContainer, box.firstChild);
        }
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    flashesContainer.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
        if (flashesContainer.children.length === 0) {
            flashesContainer.remove();
        }
    }, 5000);
}

// Генератор матриц для смешанных стратегий
document.getElementById('generateMixedMatrix').addEventListener('click', function() {
    const x = parseFloat(document.getElementById('strategyX').value);
    const y = parseFloat(document.getElementById('strategyY').value);
    const v = parseFloat(document.getElementById('gameValue').value);
    const a12 = parseFloat(document.getElementById('matrixElementA12').value);

    // Валидация ввода
    if (isNaN(x) || isNaN(y) || isNaN(v) || isNaN(a12)) {
        showFlashMessage("Все поля должны быть числами", 'error', '#mixedSaddleGenerator .second_container');
        return;
    }

    if (x < 0 || x > 1 || y < 0 || y > 1) {
        showFlashMessage("Стратегии x и y должны быть между 0 и 1", 'error', '#mixedSaddleGenerator .second_container');
        return;
    }

    if (y === 0 || (1 - x) === 0) {
        showFlashMessage("Недопустимые значения: y не может быть 0, а x не может быть 1", 'error', '#mixedSaddleGenerator .second_container');
        return;
    }

    // Отправка запроса на сервер
    fetch('/calculate_mixed_matrix', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y, v, a12 })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error); });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showFlashMessage(data.error, 'error', '#mixedSaddleGenerator .second_container');
            return;
        }

        // Отображение матрицы
        const container = document.getElementById('mixedMatrixContainer');
        container.innerHTML = '';
        
        const table = document.createElement('table');
        table.className = 'matrix';
        
        data.matrix.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell.toFixed(10).replace(/\.?0+$/, ''); // Форматирование чисел
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });
        
        container.appendChild(table);
    })
    .catch(error => {
        showFlashMessage(error.message, 'error', '#mixedSaddleGenerator .second_container');
    });
});
