var urlParams = new URLSearchParams(window.location.search);
        var message = urlParams.get('message');
        if (message) {
            alert(message);
        }

        function togglePassword(fieldId) {
            var passwordField = document.getElementById(fieldId);
            var passwordFieldType = passwordField.getAttribute("type");
            if (passwordFieldType === "password") {
                passwordField.setAttribute("type", "text");
            } else {
                passwordField.setAttribute("type", "password");
            }
        }

        const btnReg = document.getElementById("login");

        btnReg.addEventListener("click", async (event) => {
            event.preventDefault();
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const repetpassword = document.getElementById("repetpassword").value;

            if (email.length === 0 || password.length === 0 || repetpassword.length === 0) {
                alert("Заполните все поля!");
                return;
            }

            if (password !== repetpassword) {
                alert("Пароли не совпадают!");
                return;
            }

            const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
            if (!passwordPattern.test(password)) {
                alert("Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.");
                return;
            }

            const data = {
                email: email,
                password: password,
            };

            try {
                const response = await fetch("/entrance", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(data),
                });
                const result = await response.json();

                if (result.status === 'success') {
                    showSuccessAlert(result.redirect);
                } else {
                    showErrorAlert(result.message);
                }
            } catch (error) {
                alert(`Request failed: ${error.message}`);
            }
        });

        function showSuccessAlert(redirectUrl) {
            Swal.fire({
                icon: "success",
                title: "Успех",
                text: "Добро пожаловать!",
                customClass: {
                    confirmButton: "my-confirm-button",
                },
            }).then(() => {
                window.location.href = redirectUrl;
            });
        }

        function showErrorAlert(message) {
            Swal.fire({
                icon: "error",
                title: "Ошибка",
                text: message,
                confirmButtonText: "ОК",
                customClass: {
                    confirmButton: "my-error-button",
                },
            });
        }