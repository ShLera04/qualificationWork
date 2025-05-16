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

loadFiles();
loadTests();

document.getElementById("fileInputButton").addEventListener("click", function () {
    document.getElementById("fileInput").click();
});

document.getElementById("fileInput").addEventListener("change", function () {
    const fileInput = document.getElementById("fileInput");
    const fileList = document.getElementById("fileList");
    const sectionName = document.querySelector('h1.nav-item').textContent;

    Array.from(fileInput.files).forEach(file => {
        const listItem = document.createElement("div");
        listItem.classList.add("file-item");

        const fileLink = document.createElement("a");
        fileLink.textContent = file.name;
        fileLink.href = URL.createObjectURL(file);
        fileLink.target = "_blank";

        listItem.appendChild(fileLink);

        const uploadButton = document.createElement("button");
        uploadButton.textContent = "Загрузить";
        uploadButton.addEventListener("click", function () {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('section_name', sectionName);

            fetch('/upload-file', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFlashMessage("Файл успешно загружен", "success", '.box');
                    fileList.removeChild(listItem);
                    loadFiles();
                } else {
                    showFlashMessage(data.error || "Ошибка при загрузке файла", "error", '.box');
                }
            })
            .catch(error => {
                showFlashMessage("Ошибка сервера", "error", '.box');
                console.error('Error:', error);
            });
        });

        listItem.appendChild(uploadButton);
        fileList.appendChild(listItem);
    });
});

document.getElementById("createTestButton").addEventListener("click", function () {
    window.location.href = '/createTest'; 
});

document.getElementById("newQuestionButton").addEventListener("click", function () {
    window.location.href = '/addQuestion';
});

function loadFiles() {
    const sectionName = document.querySelector('h1.nav-item').textContent;

    fetch(`/get-files-by-theme?theme_name=${encodeURIComponent(sectionName)}`)
    .then(response => response.json())
    .then(fileNames => {
        const fileList = document.getElementById('downloadFileList');
        fileList.innerHTML = '';
        fileNames.forEach(fileName => {
            const listItem = document.createElement("div");
            listItem.classList.add("file-item");
            
            const fileLink = document.createElement("a");
            fileLink.href = `/download-file-by-name/${encodeURIComponent(fileName)}`;
            fileLink.textContent = fileName;
            fileLink.className = "download-link";
            
            if (fileName.toLowerCase().endsWith('.pdf')) {
                fileLink.target = "_blank";
            } else {
                fileLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    const downloadLink = document.createElement('a');
                    downloadLink.href = this.href;
                    downloadLink.download = fileName;
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                });
            }
            
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Удалить";
            deleteButton.className = "delete-button";
            deleteButton.setAttribute('data-file-name', fileName);
            deleteButton.addEventListener('click', function() {
                deleteFile(fileName);
            });
            
            listItem.appendChild(fileLink);
            listItem.appendChild(deleteButton);
            fileList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showFlashMessage("Ошибка при загрузке файлов", "error", '.box');
    });
}

function deleteFile(fileName) {
    fetch(`/delete-file-by-name/${encodeURIComponent(fileName)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage("Файл успешно удален", "success", '#material');
            loadFiles();
        } else {
            showFlashMessage(data.error || "Ошибка при удалении файла", "error", '.box');
        }
    })
    .catch(error => {
        showFlashMessage("Ошибка сервера", "error", '.box');
        console.error('Error:', error);
    });
}

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

    let flashesContainer = box.querySelector('.flashes-container');

    if (!flashesContainer) {
        flashesContainer = document.createElement('div');
        flashesContainer.className = 'flashes-container';

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

function loadTests() {
    const sectionName = document.querySelector('h1.nav-item').textContent;

    fetch(`/get-tests-by-theme?theme_name=${encodeURIComponent(sectionName)}`)
    .then(response => response.json())
    .then(tests => {
        const testsList = document.getElementById('testsList');
        testsList.innerHTML = '';
        
        tests.forEach(test => {
            const testItem = document.createElement("div");
            testItem.classList.add("file-item");
            
            const testLink = document.createElement("a");
            testLink.href = `/view-test/${test.test_id}`;
            testLink.textContent = test.test_name;
            testLink.className = "test-link";

            testLink.addEventListener('click', (e) => {
                e.preventDefault();
                openTest(test.test_name);
            });

            
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Удалить";
            deleteButton.className = "delete-button";
            deleteButton.addEventListener('click', (e) => {
                e.preventDefault();
                deleteTest(test.test_id);
            });
            
            testItem.appendChild(testLink);
            testItem.appendChild(deleteButton);
            testsList.appendChild(testItem);
        });
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showFlashMessage("Ошибка при загрузке тестов", "error", '.box');
    });
}


function deleteTest(testId) {
    
    fetch(`/delete-test/${testId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        const container = document.querySelector('.box:has(#testsList)');
        if (data.success) {
            showFlashMessage("Тест успешно удален", "success", container);
            loadTests(); 
        } else {
            showFlashMessage(data.error || "Ошибка при удалении теста", "error", container);
        }
    })
    .catch(error => {
        showFlashMessage("Ошибка сервера", "error", container);
        console.error('Error:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadFiles();
    loadTests();
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

function openTest(testName) {
    window.location.href = `/view-test/${testName}`;
}