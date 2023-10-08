/** @format */
// 當文檔載入完成後
let username = null;
let useremail = null;

document.addEventListener("DOMContentLoaded", function () {
  const authTextElement = document.querySelector(".login-in-out-button > a");
  const modal = document.getElementById("auth-modal");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const btn = document.querySelector("ul > li:nth-child(2) > a");
  const bookingPlanElement = document.getElementById("booking-plan");
  const logoElement = document.querySelector(".logo");

  // 先檢查使用者登入狀態
  fetch("/api/user/auth", {
    method: "GET",
    headers: {
      Authorization: `${localStorage.getItem("token")}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // 使用者已登入
      if (data && data.data) {
        // {data: none}
        // {data: {name: "test", email: "test", id: 1}}

        const name = data.data.name;
        const email = data.data.email;

        // 存在 localStorage 的 name
        // localStorage.setItem("name", name);
        username = name;
        useremail = email;

        console.log(username, "username");

        // 觸發一個自定義的事件
        const event = new Event("usernameUpdated");
        document.dispatchEvent(event);

        authTextElement.innerText = "登出系統";
        authTextElement.removeEventListener("click", loginEvent);
        authTextElement.addEventListener("click", logOutEvent);
      } else {
        const event = new Event("usernameNoUpdated");
        document.dispatchEvent(event);

        authTextElement.innerText = "登入/註冊";
        authTextElement.removeEventListener("click", logOutEvent);
        authTextElement.addEventListener("click", loginEvent);
      }
    })
    .catch((err) => {
      console.log("沒有回傳資料或錯誤", err);
    });

  function logOutEvent(event) {
    // 進行登出邏輯，例如清除 token
    event.preventDefault();
    modal.style.display = "none";
    localStorage.removeItem("token");
    window.location.reload();
  }

  function loginEvent(event) {
    event.preventDefault();
    modal.style.display = "flex";
  }

  logoElement.addEventListener("click", function () {
    window.location = "/";
  });

  btn.addEventListener("click", function (event) {
    event.preventDefault();
    // 顯示模態視窗
    modal.style.display = "flex";
  });

  // 關閉模態視窗
  document.getElementById("close-modal").addEventListener("click", function () {
    modal.style.display = "none";
  });

  document
    .getElementById("switch-to-register")
    .addEventListener("click", function () {
      loginForm.style.display = "none";
      registerForm.style.display = "flex";
    });

  document
    .getElementById("switch-to-login")
    .addEventListener("click", function () {
      loginForm.style.display = "flex";
      registerForm.style.display = "none";
    });

  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value.trim();

    fetch("/api/user/auth", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          document.getElementById("login-error-message").innerText =
            data.message || "登入失敗，請稍後再試。";
        } else if (data.token) {
          localStorage.setItem("token", data.token);
          window.location.reload();
        }
      });
  });

  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("register-name").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value.trim();

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;

    if (!passwordRegex.test(password)) {
      document.getElementById("register-error-message").innerText =
        "密碼設定大小寫數字，至少 8 個字元";
      return;
    }

    fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          document.getElementById("register-error-message").innerText =
            data.message || "註冊失敗，請稍後再試。";
        } else if (data.ok) {
          document.getElementById("register-error-message").innerText =
            "註冊成功";
        }
      });
  });

  bookingPlanElement.addEventListener("click", (event) => {
    event.preventDefault(); // 阻止預設的連結行為

    handleBookingClick(modal);
  });
});

function handleBookingClick(modal) {
  const token = localStorage.getItem("token");

  // console.log(token, "token");

  if (token) {
    checkTokenValidity(token).then((isValid) => {
      if (isValid) {
        window.location.href = "/booking";
      } else {
        // openLoginModal
        modal.style.display = "flex";
      }
    });
  } else {
    // openLoginModal
    modal.style.display = "flex";
  }
}

function checkTokenValidity(token) {
  return fetch("/api/user/auth", {
    headers: {
      Authorization: `${token}`,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data && data.data) {
        return true;
      } else {
        return false;
      }
    })
    .catch((err) => {
      console.error("Token validation error:", err);
      return false;
    });
}
