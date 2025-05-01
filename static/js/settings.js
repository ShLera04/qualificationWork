document.addEventListener('DOMContentLoaded', function () {
    loadThemes();
    loadStudentsForAdmin();
    loadAdmins();
    loadDirections();
    loadGroups();
    loadStudentsForDelete();
    loadStudentsForGroupChange();
    loadGroupsForChange();
    loadDirectionsForChange();
    loadStudentsForDirectionChange();

    document.getElementById("addThemeButton").addEventListener("click", function() {
        const themeName = document.getElementById("themeNameInput").value;

        fetch('/add-theme', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme_name: themeName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage(data.message || 'Тема успешно добавлена', 'success', '.box:nth-child(1)');
                loadThemes(); 
                document.getElementById("themeNameInput").value = ''; 
            } else {
                showFlashMessage(data.error || 'Ошибка при добавлении темы', 'error', '.box:nth-child(1)');
            }
        })
        .catch(error => {
            const errorMessage = error.error || "Ошибка сервера";
            showFlashMessage(errorMessage || 'Ошибка сервера', 'error', '.box:nth-child(1)');
            console.error('Error:', error);
        });
    });

    document.getElementById("addAdminButton").addEventListener("click", function () {
        const studentDropdown = document.getElementById("studentDropdownForAdmin");
        const studentName = studentDropdown.options[studentDropdown.selectedIndex].text;
        if (studentName.trim() === "") {
            showFlashMessage("Пожалуйста, выберите пользователя", "error", '.box:nth-child(2)');
            return;
        }

        fetch('/add-admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_name: studentName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage(data.message || "Администратор успешно добавлен", "success", '.box:nth-child(2)');
                loadAdmins(); 
                loadStudentsForAdmin();
                loadStudentsForDelete();
                loadStudentsForGroupChange();
                loadStudentsForDirectionChange();
            } else {
                showFlashMessage(data.error || "Ошибка при добавлении администратора", "error", '.box:nth-child(2)');
            }
        })
        .catch(error => {
            const errorMessage = error.error || "Ошибка сервера";
            showFlashMessage(errorMessage, "error", '.box:nth-child(2)');
            console.error('Error:', error);
        });
    });
    document.getElementById("deleteStudentsButton").addEventListener("click", function () {
        const directionDropdown = document.getElementById("directionDropdown");
        const groupDropdown = document.getElementById("groupDropdown");
        const directionName = directionDropdown.options[directionDropdown.selectedIndex].text;
        const groupName = groupDropdown.options[groupDropdown.selectedIndex].text;

        if (directionName.trim() === "" || groupName.trim() === "") {
            showFlashMessage("Пожалуйста, выберите направление подготовки и группу", "error", '#deleteStudentsBox');
            return;
        }

        fetch('/delete-students', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ direction_name: directionName, group_name: groupName })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showFlashMessage(data.message || "Студенты успешно удалены", "success", '#deleteStudentsBox');
                loadAdmins(); 
                loadStudentsForAdmin(); 
                loadStudentsForDelete();
                loadStudentsForGroupChange();
                loadStudentsForDirectionChange();
                loadDirectionsForChange();
            } else {
                showFlashMessage(data.message, "error", '#deleteStudentsBox');
            }
        })
        .catch(error => {
            const errorMessage = error.error || "Ошибка сервера";
            showFlashMessage(errorMessage, "error", '#deleteStudentsBox');
            console.error('Error:', error);
        });
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

function loadThemes() {
    fetch('/get-themes')
    .then(response => response.json())
    .then(themes => {
        const themeList = document.getElementById('themeList');
        themeList.innerHTML = '';
        themes.forEach(theme => {
            const listItem = document.createElement("div");
            listItem.classList.add("theme-item");
            listItem.innerHTML = `
                <span>${theme.name}</span>
                <button class="delete-theme-button" data-theme-name="${theme.name}">Удалить</button>
            `;
            themeList.appendChild(listItem);
        });

        document.querySelectorAll('.delete-theme-button').forEach(button => {
            button.addEventListener('click', function () {
                const themeName = this.getAttribute('data-theme-name');
                deleteTheme(themeName);
            });
        });
    })
    .catch(error => console.error('Ошибка:', error));
}

function deleteTheme(themeName) {
    fetch(`/delete-theme/${encodeURIComponent(themeName)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        const box = document.querySelector('.box:nth-child(1)');
        let flashesContainer = box.querySelector('.flashes-container');

        if (!flashesContainer) {
            flashesContainer = document.createElement('div');
            flashesContainer.className = 'flashes-container';
            box.insertBefore(flashesContainer, box.querySelector('.input-container'));
        }

        if (data.success) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success';
            alertDiv.textContent = data.message || `Тема "${themeName}" успешно удалена`;
            flashesContainer.appendChild(alertDiv);

            setTimeout(() => {
                alertDiv.remove();
                if (flashesContainer.children.length === 0) {
                    flashesContainer.remove();
                }
            }, 5000);

            loadThemes();
        } else {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-error';
            alertDiv.textContent = data.error || 'Ошибка при удалении темы';
            flashesContainer.appendChild(alertDiv);

            setTimeout(() => {
                alertDiv.remove();
                if (flashesContainer.children.length === 0) {
                    flashesContainer.remove();
                }
            }, 5000);
        }
    })
    .catch(error => {
        const box = document.querySelector('.box:nth-child(1)');
        let flashesContainer = box.querySelector('.flashes-container');

        if (!flashesContainer) {
            flashesContainer = document.createElement('div');
            flashesContainer.className = 'flashes-container';
            box.insertBefore(flashesContainer, box.querySelector('.input-container'));
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-error';
        alertDiv.textContent = 'Ошибка сервера при удалении темы';
        flashesContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
            if (flashesContainer.children.length === 0) {
                flashesContainer.remove();
            }
        }, 5000);

        console.error('Ошибка:', error);
    });
}

function loadAdmins() {
    fetch('/get-admins')
    .then(response => response.json())
    .then(admins => {
        const adminList = document.getElementById('adminList');
        adminList.innerHTML = '';
        admins.forEach(admin => {
            const listItem = document.createElement("div");
            listItem.classList.add("theme-item");
            listItem.innerHTML = `
                <span>${admin.name}</span>
                <button class="delete-admin-button" data-admin-name="${admin.name}">Удалить</button>
            `;
            adminList.appendChild(listItem);
        });

        document.querySelectorAll('.delete-admin-button').forEach(button => {
            button.addEventListener('click', function () {
                const adminName = this.getAttribute('data-admin-name');
                deleteAdmin(adminName);
            });
        });
    })
    .catch(error => console.error('Ошибка:', error));
}

function deleteAdmin(adminName) {
    fetch(`/delete-admin/${encodeURIComponent(adminName)}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Ошибка при удалении администратора');
            });
        }
        return response.json();
    })
    .then(data => {
        const container = document.querySelector('.box:nth-child(2)');
        const flashesContainer = container.querySelector('.flashes-container') ||
            (() => {
                const fc = document.createElement('div');
                fc.className = 'flashes-container';
                container.insertBefore(fc, container.children[1]);
                return fc;
            })();

        const alertDiv = document.createElement('div');
        alertDiv.className = data.success ? 'alert alert-success' : 'alert alert-error';
        alertDiv.textContent = data.success
            ? data.message || `Администратор успешно удален`
            : data.error || 'Ошибка при удалении администратора';

        flashesContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
            if (flashesContainer.children.length === 0) {
                flashesContainer.remove();
            }
        }, 5000);

        if (data.success) {
            loadAdmins(); 
            loadStudentsForAdmin();
            loadStudentsForDelete();
            loadStudentsForGroupChange();
            loadStudentsForDirectionChange();
            loadDirectionsForChange();
        }
    })
    .catch(error => {
        const container = document.querySelector('.box:nth-child(2)');
        const flashesContainer = container.querySelector('.flashes-container') ||
            (() => {
                const fc = document.createElement('div');
                fc.className = 'flashes-container';
                container.insertBefore(fc, container.children[1]);
                return fc;
            })();

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-error';
        alertDiv.textContent = error.message || 'Ошибка сети при удалении администратора';
        flashesContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
            if (flashesContainer.children.length === 0) {
                flashesContainer.remove();
            }
        }, 5000);

        console.error('Ошибка:', error);
    });
}


function loadStudentsForAdmin() {
    fetch('/get-students-for-admin')
    .then(response => response.json())
    .then(students => {
        const studentDropdown = document.getElementById('studentDropdownForAdmin');
        studentDropdown.innerHTML = '<option disabled selected value="">Выберите пользователя</option>';
        if (students.length === 0) {
            const defaultOption = document.createElement("option");
            defaultOption.value = '';
            defaultOption.disabled = true; 
            defaultOption.selected = true;
            defaultOption.text = 'Нет доступных студентов';
            studentDropdown.appendChild(defaultOption);
        } else {
            students.forEach(student => {
                const option = document.createElement("option");
                option.value = student.name;
                option.text = student.name;
                studentDropdown.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function loadDirections() {
    fetch('/get-directions')
    .then(response => response.json())
    .then(directions => {
        const directionDropdown = document.getElementById('directionDropdown');
        directionDropdown.innerHTML = '<option disabled selected value="">Выберите направление</option>';
        directions.forEach(direction => {
            const option = document.createElement("option");
            option.value = direction.name;
            option.text = direction.name;
            directionDropdown.appendChild(option);
        });
    })
    .catch(error => console.error('Ошибка:', error));
}

function loadGroups() {
    fetch('/get-groups')
    .then(response => response.json())
    .then(groups => {
        const groupDropdown = document.getElementById('groupDropdown');
        groupDropdown.innerHTML = '<option disabled selected value="">Выберите группу</option>';
        groups.forEach(group => {
            const option = document.createElement("option");
            option.value = group.name;
            option.text = group.name;
            groupDropdown.appendChild(option);
        });
    })
    .catch(error => console.error('Ошибка:', error));
}
document.getElementById("deleteStudentButton").addEventListener("click", function () {
    const studentDropdown = document.getElementById("studentDropdownForDelete");

    if (studentDropdown.options.length === 0) {
        showFlashMessage("Список студентов пуст", "error", '#deleteStudentBox');
        return;
    }

    const studentName = studentDropdown.options[studentDropdown.selectedIndex].text;

    if (studentName.trim() === "") {
        showFlashMessage("Пожалуйста, выберите студента", "error", '#deleteStudentBox');
        return;
    }

    fetch(`/delete-student/${encodeURIComponent(studentName)}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message || "Пользователь успешно удален", "success", '#deleteStudentBox');
            loadStudentsForDelete();
            loadStudentsForAdmin();
            loadStudentsForGroupChange();
            loadStudentsForDirectionChange();

        } else {
            showFlashMessage(data.message, "error", '#deleteStudentBox');
        }
    })
    .catch(error => {
        const errorMessage = error.error || "Ошибка сервера";
        showFlashMessage(errorMessage, "error", '#deleteStudentBox');
        console.error('Error:', error);
    });
});

function loadStudentsForDelete() {
    fetch('/get-students-for-admin')
    .then(response => response.json())
    .then(students => {
        const studentDropdown = document.getElementById('studentDropdownForDelete');
        studentDropdown.innerHTML = '<option disabled selected value="">Выберите пользователя</option>';
        if (students.length === 0) {
            const defaultOption = document.createElement("option");
            defaultOption.value = '';
            defaultOption.disabled = true; 
            defaultOption.selected = true;
            defaultOption.text = 'Нет доступных студентов';
            studentDropdown.appendChild(defaultOption);
        } else {
            students.forEach(student => {
                const option = document.createElement("option");
                option.value = student.name;
                option.text = student.name;
                studentDropdown.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Ошибка:', error));
}
document.getElementById("changeStudentGroupButton").addEventListener("click", function () {
        const studentDropdown = document.getElementById("studentDropdownForGroupChange");
        const groupDropdown = document.getElementById("groupDropdownForChange");

        const studentName = studentDropdown.options[studentDropdown.selectedIndex].text;
        const newGroupName = groupDropdown.options[groupDropdown.selectedIndex].text;

        if (studentName.trim() === "" || newGroupName.trim() === "") {
            showFlashMessage("Пожалуйста, выберите студента и новую группу", "error", '#changeStudentGroupBox');
            return;
        }

        fetch('/change-student-group', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ student_name: studentName, new_group_name: newGroupName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage(data.message, "success", '#changeStudentGroupBox');
                loadStudentsForAdmin();
                loadStudentsForGroupChange();
                loadStudentsForDirectionChange();
                loadStudentsForDelete();
            } else {
                showFlashMessage(data.error || "Ошибка при изменении группы", "error", '#changeStudentGroupBox');
            }
        })
        .catch(error => {
            const errorMessage = error.error || "Ошибка сервера";
            showFlashMessage(errorMessage, "error", '#changeStudentGroupBox');
            console.error('Error:', error);
        });
    });
        function loadStudentsForGroupChange() {
    fetch('/get-students-for-admin')
    .then(response => response.json())
    .then(students => {
        const studentDropdown = document.getElementById('studentDropdownForGroupChange');
        studentDropdown.innerHTML = '<option disabled selected value="">Выберите пользователя</option>';
        if (students.length === 0) {
            const defaultOption = document.createElement("option");
            defaultOption.value = '';
            defaultOption.disabled = true; 
            defaultOption.selected = true;
            defaultOption.text = 'Нет доступных студентов';
            studentDropdown.appendChild(defaultOption);
        } else {
            students.forEach(student => {
                const option = document.createElement("option");
                option.value = student.name;
                option.text = student.name;
                studentDropdown.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Ошибка:', error));
}
function loadGroupsForChange() {
    fetch('/get-groups')
    .then(response => response.json())
    .then(groups => {
        const groupDropdown = document.getElementById('groupDropdownForChange');
        groupDropdown.innerHTML = '<option disabled selected value="">Выберите группу</option>'; 
        if (groups.length === 0) {
            const defaultOption = document.createElement("option");
            defaultOption.value = '';
            defaultOption.disabled = true;
            defaultOption.selected = true;
            defaultOption.text = 'Нет доступных групп';
            groupDropdown.appendChild(defaultOption);
        } else {
            groups.forEach(group => {
                const option = document.createElement("option");
                option.value = group.name;
                option.text = group.name;
                groupDropdown.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

document.getElementById("changeStudentDirectionButton").addEventListener("click", function () {
    const studentDropdown = document.getElementById("studentDropdownForDirectionChange");
    const directionDropdown = document.getElementById("directionDropdownForChange");

    const studentName = studentDropdown.options[studentDropdown.selectedIndex].text;
    const newDirectionName = directionDropdown.options[directionDropdown.selectedIndex].text;

    if (studentName.trim() === "" || newDirectionName.trim() === "") {
        showFlashMessage("Пожалуйста, выберите студента и новое направление", "error", '#changeStudentDirectionBox');
        return;
    }

    fetch('/change-student-direction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ student_name: studentName, new_direction_name: newDirectionName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message ||"Направление успешно изменено", "success", '#changeStudentDirectionBox');
            loadStudentsForAdmin();
            loadStudentsForGroupChange();
            loadStudentsForDirectionChange();
            loadStudentsForDelete();
        } else {
            showFlashMessage(data.error || "Ошибка при изменении направления", "error", '#changeStudentDirectionBox');
        }
    })
    .catch(error => {
        const errorMessage = error.error || "Ошибка сервера";
        showFlashMessage(errorMessage || "Ошибка сервера", "error", '#changeStudentDirectionBox');
        console.error('Error:', error);
    });
});

function loadDirectionsForChange() {
    fetch('/get-directions')
    .then(response => response.json())
    .then(directions => {
        const directionDropdown = document.getElementById('directionDropdownForChange');
        directionDropdown.innerHTML = '<option disabled selected value="">Выберите направление</option>';
        directions.forEach(direction => {
            const option = document.createElement("option");
            option.value = direction.name;
            option.text = direction.name;
            directionDropdown.appendChild(option);
        });
    })
    .catch(error => console.error('Ошибка:', error));
}

function loadStudentsForDirectionChange() {
    fetch('/get-students-for-admin')
    .then(response => response.json())
    .then(students => {
        const studentDropdown = document.getElementById('studentDropdownForDirectionChange');
        studentDropdown.innerHTML = '<option disabled selected value="">Выберите пользователя</option>';
        if (students.length === 0) {
            const defaultOption = document.createElement("option");
            defaultOption.value = '';
            defaultOption.text = 'Нет доступных студентов';
            defaultOption.disabled = true; // Добавляем атрибут disabled
            defaultOption.selected = true;
            studentDropdown.appendChild(defaultOption);
        } else {
            students.forEach(student => {
                const option = document.createElement("option");
                option.value = student.name;
                option.text = student.name;
                studentDropdown.appendChild(option);
            });
        }
    })
    .catch(error => console.error('Ошибка:', error));
}