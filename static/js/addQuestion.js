const burgerMenu = document.getElementById('burgerMenu');
const menuOverlay = document.getElementById('menuOverlay');
const closeMenu = document.getElementById('closeMenu');

function setupImagePreview() {
    const imageInput = document.getElementById('question-image');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');
    
    imageInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                removeImageBtn.style.display = 'inline-block';
            }
            
            reader.readAsDataURL(this.files[0]);
        }
    });
}

function removeImage() {
    const imageInput = document.getElementById('question-image');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');
    
    imageInput.value = '';
    imagePreview.src = '#';
    imagePreview.style.display = 'none';
    removeImageBtn.style.display = 'none';
}

// Получение информации о пользователе
fetch('/get_user_info')
.then(response => response.json())
.then(data => {
    if(data.logged_in) {
        document.querySelector('.username').textContent = data.login;
    }
});

// Заполнение выпадающих списков
async function populateSelectOptions(selectId, endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        const select = document.getElementById(selectId);
        data.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.name;
            opt.text = option.name;
            select.add(opt);
        });
    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    populateSelectOptions('theme', '/get-themes');
        
    document.getElementById('fileInputButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', function() {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        
        Array.from(this.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-name">${file.name}</span>
                <button type="button" class="delete-button" onclick="this.parentNode.remove()">×</button>
            `;
            fileList.appendChild(fileItem);
        });
    });
    
    // Обработчики для бургер-меню
    burgerMenu.addEventListener('click', () => {
        menuOverlay.classList.toggle('active');
    });

    closeMenu.addEventListener('click', () => {
        menuOverlay.classList.remove('active');
    });

    menuOverlay.addEventListener('click', (event) => {
        if (event.target === menuOverlay) {
            menuOverlay.classList.remove('active');
        }
    });

    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuOverlay.classList.remove('active');
        });
    });
    
    document.getElementById('testForm').addEventListener('submit', async function(event) {
        event.preventDefault();
    
        const form = document.getElementById('testForm');
        const formData = new FormData(form);
        const questionType = document.getElementById('question-type').value;
    
        // Добавляем варианты ответов в FormData
        if (questionType === 'single') {
            const options = document.querySelectorAll('.option-container');
            options.forEach((option, index) => {
                const textInput = option.querySelector('input[type="text"]');
                formData.append(`option-${index+1}`, textInput.value);
    
                const radioInput = option.querySelector('input[type="radio"]');
                if (radioInput.checked) {
                    formData.append('correct-option', index+1);
                }
            });
        }
    
        // Добавляем файлы в FormData
        const fileInput = document.getElementById('fileInput');
        if (fileInput.files.length > 0) {
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append('fileInput', fileInput.files[i]);
            }
        }
    
        try {
            // Отладочная информация - выводим содержимое FormData
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }
    
            const response = await fetch('/create-question', {
                method: 'POST',
                body: formData
            });
    
            const result = await response.json();
    
            if (result.status === 'success') {
                showFlashMessage('Вопрос успешно добавлен!', 'success');
                resetForm();
            } else {
                showFlashMessage(result.message || 'Ошибка при добавлении вопроса', 'error');
            }
        } catch (error) {
            console.error('Ошибка при отправке формы:', error);
            showFlashMessage('Произошла ошибка при отправке формы', 'error');
        }
    });
    
    
    
});

// Переключение полей в зависимости от типа вопроса
function toggleQuestionFields() {
    const questionType = document.getElementById('question-type').value;
    
    // Скрываем все динамические поля
    document.querySelectorAll('.dynamic-fields').forEach(field => {
        field.style.display = 'none';
    });
    
    // Показываем нужные поля
    if (questionType === 'value') {
        document.getElementById('value-fields').style.display = 'block';
    } else if (questionType === 'single') {
        document.getElementById('single-fields').style.display = 'block';
    }
}

function addOption() {
    const optionsContainer = document.getElementById('options-container');
    const optionIndex = optionsContainer.querySelectorAll('.option-container').length + 1;
    
    const optionDiv = document.createElement('div');
    optionDiv.className = 'option-container';
    optionDiv.innerHTML = `
        <input type="radio" name="correct-option" value="${optionIndex}">
        <input type="text" placeholder="Вариант ответа ${optionIndex}" required>
        <button type="button" onclick="removeOption(this)">×</button>
    `;
    
    const addButton = optionsContainer.querySelector('.add-option-btn');
    optionsContainer.insertBefore(optionDiv, addButton);
}

function removeOption(button) {
    const optionDiv = button.closest('.option-container');
    optionDiv.remove();
    
    // Обновляем нумерацию оставшихся вариантов
    const options = document.querySelectorAll('.option-container');
    options.forEach((option, index) => {
        const radio = option.querySelector('input[type="radio"]');
        const textInput = option.querySelector('input[type="text"]');
        
        radio.value = index + 1;
        textInput.placeholder = `Вариант ответа ${index + 1}`;
    });
}

async function submitForm(event) {
    event.preventDefault();
    
    const form = document.getElementById('testForm');
    const formData = new FormData(form);
    const questionType = document.getElementById('question-type').value;
    
    // Проверка заполнения полей в зависимости от типа вопроса
    if (questionType === 'value') {
        const correctValue = document.getElementById('correct-value').value;
        if (!correctValue) {
            alert('Пожалуйста, введите правильный ответ');
            return;
        }
    } else if (questionType === 'single') {
        const options = document.querySelectorAll('.option-container');
        if (options.length < 2) {
            alert('Добавьте как минимум 2 варианта ответа');
            return;
        }
        
        const selectedOption = document.querySelector('input[name="correct-option"]:checked');
        if (!selectedOption) {
            alert('Пожалуйста, выберите правильный вариант ответа');
            return;
        }
        
        // Добавляем варианты ответов в formData
        options.forEach((option, index) => {
            const textInput = option.querySelector('input[type="text"]');
            formData.append('options[]', textInput.value);
            
            if (option.querySelector('input[type="radio"]:checked')) {
                formData.append('correct_option', index + 1);
            }
        });
    }
    
    try {
        const response = await fetch('/create-question', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            alert('Вопрос успешно добавлен!');
            form.reset();
            removeImage(); // Сбрасываем изображение
            document.querySelectorAll('.dynamic-fields').forEach(field => {
                field.style.display = 'none';
            });
            document.getElementById('options-container').querySelectorAll('.option-container').forEach(option => {
                option.remove();
            });
        } else {
            alert('Ошибка: ' + (result.message || 'Не удалось добавить вопрос'));
        }
    } catch (error) {
        console.error('Ошибка при отправке формы:', error);
        alert('Произошла ошибка при отправке формы');
    }
}
function showFlashMessage(message, type) {
    const flashesDiv = document.querySelector('.flashes');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    flashesDiv.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
function uploadFile(file, listItem) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('question_id', 'new'); // Или другой идентификатор вопроса
    
    fetch('/upload-question-file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage("Файл успешно загружен", "success");
            listItem.querySelector('.upload-button').style.display = 'none';
        } else {
            showFlashMessage(data.error || "Ошибка при загрузке файла", "error");
        }
    })
    .catch(error => {
        showFlashMessage("Ошибка сервера", "error");
        console.error('Error:', error);
    });
}

function resetForm() {
    const form = document.getElementById('testForm');
    form.reset();
    
    // Очистка динамических полей
    document.querySelectorAll('.dynamic-fields').forEach(field => {
        field.style.display = 'none';
    });
    
    // Удаление всех вариантов ответа
    document.getElementById('options-container').querySelectorAll('.option-container').forEach(option => {
        option.remove();
    });
    
    // Очистка списка файлов
    document.getElementById('fileList').innerHTML = '';
    document.getElementById('fileInput').value = '';
}