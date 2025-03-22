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


    // const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    // if (!passwordPattern.test(password)) {
    //     alert("Пароль должен содержать минимум 8 символов, включая заглавные и строчные буквы, цифры и специальные символы.");
    //     return;
    // }
});

