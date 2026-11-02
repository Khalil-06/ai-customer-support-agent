const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("loginButton");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";
    loginMessage.textContent = "";

    try {

        const data = await apiRequest("/login", {
            method: "POST",
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        localStorage.setItem(
            "user",
            JSON.stringify(data.user)
        );

        loginMessage.textContent = "Login successful!";

        window.location.href = "dashboard.html";

    } catch (error) {

        loginMessage.textContent = error.message;

        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
});