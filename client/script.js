//Shared JS file that handles login, register, enrollment, and profile features
const baseUrl = "http://localhost:5000"; // Update with deployment URL if needed

/* -----------------------------------
   LOGIN FORM LOGIC (index.html)
------------------------------------ */
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.onsubmit = async (e) => {
    e.preventDefault();

    const id = document.getElementById("id-input").value;
    const password = document.getElementById("password-input").value;
    const errorMessage = document.getElementById("error-message");

    errorMessage.style.display = "none";

    try {
      const res = await fetch(`${baseUrl}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        errorMessage.style.display = "block";
        errorMessage.textContent = data.message || "Unable to sign in.";
        return;
      }

      // Redirect to info page on successful login
      window.location.href = "/client/information";
    } catch {
      errorMessage.style.display = "block";
      errorMessage.textContent = "Server error. Please try again.";
    }
  };
}

/* -----------------------------------
   REGISTER FORM LOGIC (index.html)
------------------------------------ */
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.onsubmit = async (e) => {
    e.preventDefault();

    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    const res = await fetch(`${baseUrl}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    alert(data.message);
  };
}

/* -----------------------------------
   ENROLLMENT FORM LOGIC (information/index.html)
------------------------------------ */
const enrollForm = document.getElementById("enroll-form");
if (enrollForm) {
  enrollForm.onsubmit = async (e) => {
    e.preventDefault();

    const classCode = document.getElementById("class-code").value;

    const res = await fetch(`${baseUrl}/enroll`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ classCode }),
    });

    const data = await res.json();
    alert(data.message);
  };
}

/* -----------------------------------
   PROFILE UPDATE (profile/index.html)
------------------------------------ */
const profileForm = document.getElementById("profile-form");
if (profileForm) {
  profileForm.onsubmit = async (e) => {
    e.preventDefault();

    const fullName = document.getElementById("full-name").value;
    const bio = document.getElementById("bio").value;

    const res = await fetch(`${baseUrl}/update-profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fullName, bio }),
    });

    const data = await res.json();
    alert(data.message);
  };
}

/* -----------------------------------
   VIEW PROFILE LOGIC (profile/index.html)
------------------------------------ */
const viewProfileBtn = document.getElementById("view-profile-btn");
if (viewProfileBtn) {
  viewProfileBtn.onclick = async () => {
    const res = await fetch(`${baseUrl}/profile`);
    const data = await res.json();

    const info = `
      <p><strong>Name:</strong> ${data.fullName}</p>
      <p><strong>Bio:</strong> ${data.bio}</p>
    `;
    document.getElementById("profile-info").innerHTML = info;
  };
}
