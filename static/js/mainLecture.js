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

        

        // Открываем модальное окно
        openModalButton.addEventListener('click', () => {
            modal.style.display = 'flex'; // Показываем окно с flex
        });

        // Закрываем модальное окно
        closeModalButton.addEventListener('click', () => {
            modal.style.display = 'none'; // Скрываем окно
        });

        openAdminModalButton.addEventListener('click', () => {
            adminModal.style.display = 'flex';
        });

        // Закрываем второе модальное окно
        closeAdminModalButton.addEventListener('click', () => {
            adminModal.style.display = 'none';
        });

        // Закрытие модального окна при клике вне его
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
            if (event.target === adminModal) {
                adminModal.style.display = 'none';
            }
        });

        // Добавляем тему
        addTopicButton.addEventListener('click', async () => {
            const topic = topicInput.value;

            if (topic) {
                try {
                    const response = await fetch('/add-theme', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ theme_name: topic })
                    });

                    const result = await response.json();
                    if (result.status === 'success') {
                        // Создаем новую карточку
                        const newCard = document.createElement('div');
                        newCard.classList.add('cards');
                        newCard.innerHTML = `
                            <p>Раздел №${cardsContainer.children.length + 1}</p>
                            <p>Тема:</p>
                            <a href="../page${cardsContainer.children.length + 1}">
                                <p>"${result.theme.name}"</p>
                            </a>
                        `;

                        // Добавляем новую карточку в контейнер
                        cardsContainer.appendChild(newCard);

                        // Очищаем поле ввода
                        topicInput.value = '';

                        // Закрываем модальное окно
                        modal.style.display = 'none';

                        // Обновляем состояние кнопок прокрутки
                        updateButtons();
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Произошла ошибка при добавлении темы.');
                }
            }
        });

        // Добавляем админа
        addAdminButton.addEventListener('click', async () => {
            const adminName = adminSelect.value;

            if (adminName) {
                try {
                    const response = await fetch('/add-admin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ admin_name: adminName })
                    });

                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('Админ успешно добавлен!');
                        adminSelect.value = '';
                        adminModal.style.display = 'none';
                    } else {
                        alert(result.message);
                    }
                } catch (error) {
                    console.error('Ошибка:', error);
                    alert('Произошла ошибка при добавлении админа.');
                }
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
            if (result.length > 0) {
                result.forEach(point => {
                    resultsContainer.innerHTML += `(${point[0]}, ${point[1]})<br>`;
                });
            } else {
                if (title === 'Седловые точки') {
                    resultsContainer.innerHTML += 'Седловые точки не найдены.<br>';
                } else if (title === 'Равновесие по Нэшу') {
                    resultsContainer.innerHTML += 'Равновесие по Нэшу не найдено.<br>';
                } else if (title === 'Оптимальность по Парето') {
                    resultsContainer.innerHTML += 'Парето-оптимальные точки не найдены.<br>';
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
                // Преобразуем результат в формат [ [x, y], [x, y], ... ]
                const formattedResult = result.map(point => [point[0], point[1]]);
                displayResult(formattedResult, title);
            })
            .catch(error => console.error('Error:', error));
        }

        document.getElementById('optionSelect').addEventListener('change', function() {
            const selectedOption = this.value;
            if (selectedOption === 'saddlePoints') {
                const matrix = getMatrix('matrixContainer');  // Матрица A
                sendRequest('/saddle_points', { matrix: matrix }, 'Седловые точки');
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
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/get-themess')
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

        document.addEventListener('DOMContentLoaded', function() {
            fetch('/get-regular-users')
                .then(response => response.json())
                .then(users => {
                    const adminSelect = document.getElementById('adminSelect');
                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.value;
                        option.textContent = user.text;
                        adminSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Ошибка:', error));
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
            const themeName = card.querySelector('a p').textContent.toLowerCase();
            if (themeName.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });