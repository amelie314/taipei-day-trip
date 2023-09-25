/** @format */

// 當文檔載入完成後
document.addEventListener("DOMContentLoaded", function () {
  const authTextElement = document.querySelector(".login-in-out-button > a");
  // 先檢查使用者登入狀態
  fetch("/api/user/auth", {
    headers: {
      Authorization: `${localStorage.getItem("token")}`, // 若有 token 存在 localStorage，加入到請求頭
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.data) {
        // 使用者已登入
        authTextElement.innerText = "登出系統";
        authTextElement.removeEventListener("click", loginEvent);
        authTextElement.addEventListener("click", logOutEvent);
      }
    })
    .catch((err) => {
      authTextElement.innerText = "登入/註冊";
      authTextElement.removeEventListener("click", logOutEvent);
      authTextElement.addEventListener("click", loginEvent);
    });
  function logOutEvent(event) {
    event.preventDefault();
    // 進行登出邏輯，例如清除 token
    modal.style.display = "none";

    localStorage.removeItem("token");
    window.location.reload();
  }

  function loginEvent(event) {
    event.preventDefault();
    // 顯示登入/註冊模態視窗
    modal.style.display = "flex";
  }

  // 找到具有 'logo' 類別的 h1 元素
  const logoElement = document.querySelector(".logo");

  // 為這個 h1 元素添加 click 事件監聽器
  logoElement.addEventListener("click", function () {
    // 使用 urlApi 進行導航
    // window.location = urlApi;
    window.location = "/";
  });

  const modal = document.getElementById("auth-modal");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const btn = document.querySelector("ul > li:nth-child(2) > a");

  // 顯示模態視窗
  btn.addEventListener("click", function (event) {
    event.preventDefault();
    modal.style.display = "block";
  });

  // 關閉模態視窗
  document.getElementById("close-modal").addEventListener("click", function () {
    modal.style.display = "none";
  });

  // 切換到註冊表單
  document
    .getElementById("switch-to-register")
    .addEventListener("click", function () {
      loginForm.style.display = "none";
      registerForm.style.display = "block";
    });

  // 切換到登入表單
  document
    .getElementById("switch-to-login")
    .addEventListener("click", function () {
      loginForm.style.display = "block";
      registerForm.style.display = "none";
    });

  // 登入表單提交
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
          // 登入成功
          // 將 token 存到 localStorage
          localStorage.setItem("token", data.token);
          // 重新載入頁面
          window.location.reload();
        }
      });
  });

  // 註冊表單提交
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const name = document.getElementById("register-name").value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value.trim();

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
    // 大小寫數字，至少 8 個字元
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
});
