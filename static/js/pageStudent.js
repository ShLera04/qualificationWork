loadFiles();
loadTests();
document.getElementById("createTestButton").addEventListener("click", function () {
    window.location.href = 'formula';
});

document.getElementById("newQuestionButton").addEventListener("click", function () {
    window.location.href = 'test';
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
            
            const link = document.createElement("a");
            link.href = `/download-file-by-name/${encodeURIComponent(fileName)}`;
            link.textContent = fileName;
            link.className = "download-link";
            
            if (fileName.toLowerCase().endsWith('.pdf')) {
                link.target = "_blank";
            } else {
                link.download = fileName;
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const downloadLink = document.createElement('a');
                    downloadLink.href = this.href;
                    downloadLink.download = fileName;
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                });
            }

            const openButton = document.createElement("button");
            openButton.textContent = "Открыть";
            openButton.className = "delete-button";
            openButton.setAttribute('data-file-name', fileName);
            openButton.addEventListener('click', function() {
                handleFileOpen(fileName);
            });
            
            listItem.appendChild(link);
            listItem.appendChild(openButton);
            fileList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showFlashMessage("Ошибка при загрузке файлов", "error", '.box');
    });
}
function handleFileClick(event, fileName) {
    event.preventDefault(); 
    const newWindow = window.open(`/download-file-by-name/${encodeURIComponent(fileName)}`, '_blank');

    if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
        const link = document.createElement('a');
        link.href = `/download-file-by-name/${encodeURIComponent(fileName)}`;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
function handleFileOpen(fileName) {
    const url = `/download-file-by-name/${encodeURIComponent(fileName)}`;
    
    if (!fileName.toLowerCase().endsWith('.pdf')) {
        forceDownload(url, fileName);
    } else {
        const newWindow = window.open(url, '_blank');
        if (!newWindow || newWindow.closed) {
            forceDownload(url, fileName);
        }
    }
}

function forceDownload(url, fileName) {
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
        function loadTests() {
    const sectionName = document.querySelector('h1.nav-item').textContent;

    fetch(`/get-tests-by-theme?theme_name=${encodeURIComponent(sectionName)}`)
    .then(response => response.json())
    .then(tests => {
        const testsList = document.getElementById('testsListStudent');
        testsList.innerHTML = '';
        
        tests.forEach(test => {
            const testItem = document.createElement("div");
            testItem.classList.add("file-item");
            
            const testLink = document.createElement("a");
            testLink.href = `/view-test/${test.test_id}`;
            testLink.textContent = test.test_name;
            testLink.className = "test-link";
            
            const openButton = document.createElement("button");
            openButton.textContent = "Открыть";
            openButton.className = "delete-button";
            openButton.addEventListener('click', (e) => {
                e.preventDefault();
                openTest(test.test_id);
            });

            testItem.appendChild(testLink);
            testItem.appendChild(openButton);
            testsList.appendChild(testItem);
        });
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showFlashMessage("Ошибка при загрузке тестов", "error", '.box');
    });
}
document.addEventListener('DOMContentLoaded', function() {
    loadFiles();
    loadTests();
});

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