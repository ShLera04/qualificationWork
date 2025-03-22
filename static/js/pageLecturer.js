document.getElementById("fileInput").addEventListener("change", function () {
    const fileInput = document.getElementById("fileInput");
    const fileList = document.getElementById("fileList");

    // Проходим по каждому выбранному файлу и добавляем его в список
    Array.from(fileInput.files).forEach(file => {
        // Создаем элемент для отображения файла
        const listItem = document.createElement("div");
        listItem.classList.add("file-item");

        // Создаем ссылку для скачивания файла
        // const fileLink = document.createElement("a");
        // fileLink.textContent = file.name; 


        // const reader = new FileReader();
        // reader.onload = function(event) {
        //     const fileURL = URL.createObjectURL(file);
        //     fileLink.href = fileURL;
        //     fileLink.download = file.name; 
        // };
        // reader.readAsDataURL(file);
        // Создаем ссылку для открытия файла в новой вкладке
        const fileLink = document.createElement("a");
        fileLink.textContent = file.name; // Указываем имя файла
        fileLink.href = URL.createObjectURL(file);
        fileLink.target = "_blank"; // Открываем ссылку в новой вкладке

        // Добавляем ссылку в элемент списка
        listItem.appendChild(fileLink);

        // Создаем кнопку для удаления файла
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Удалить";
        deleteButton.addEventListener("click", function () {
            // Удаляем элемент из списка
            fileList.removeChild(listItem);
            // Удаляем URL-адрес файла
            URL.revokeObjectURL(fileLink.href);
        });

        // Добавляем кнопку в элемент списка
        listItem.appendChild(deleteButton);

        // Добавляем элемент в список файлов
        fileList.appendChild(listItem);
    });
});

// Обработчик события для кнопки "Составить тест"
document.getElementById("createTestButton").addEventListener("click", function () {
    window.location.href = 'formula';
});
document.getElementById("newQuestionButton").addEventListener("click", function () {
    window.location.href = 'test';
});