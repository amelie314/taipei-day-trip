/** @format */

document.addEventListener("DOMContentLoaded", function () {
  // document.querySelector(".name").textContent = localStorage.getItem("name");

  document.addEventListener("usernameNoUpdated", function () {
    window.location.href = "/";
  });
  // 在 booking.js
  document.addEventListener("usernameUpdated", function () {
    document.querySelector(".welcome-title").textContent = username;
    // 輸入 input 的值
    document.querySelector("#user-name").value = username;
    document.querySelector("#user-email").value = useremail;
    getBooking();
    tappayPay();
  });

  function tappayPay() {
    // console.log("tappayPay");
    TPDirect.setupSDK(appId, appKey, "sandbox");

    // console.log(appId, appKey);

    // 選填 CCV Example
    let fields = {
      number: {
        // css selector
        element: "#card-number",
        placeholder: "**** **** **** ****",
      },
      expirationDate: {
        // DOM object
        element: "#card-expiration-date",
        placeholder: "MM / YY",
      },
      ccv: {
        element: "#card-ccv",
        placeholder: "後三碼",
      },
    };
    TPDirect.card.setup({
      fields: fields,
      // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
      styles: {
        // Style all elements
        input: {
          color: "gray",
        },
        // Styling ccv field
        "input.ccv": {
          // 'font-size': '16px'
        },
        // Styling expiration-date field
        "input.expiration-date": {
          // 'font-size': '16px'
        },
        // Styling card-number field
        "input.card-number": {
          // 'font-size': '16px'
        },
        // style focus state
        ":focus": {
          // 'color': 'black'
        },
        // style valid state
        ".valid": {
          color: "green",
        },
        // style invalid state
        ".invalid": {
          color: "red",
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        "@media screen and (max-width: 400px)": {
          input: {
            color: "orange",
          },
        },
      },
      isMaskCreditCardNumber: true,
      maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11,
      },
    });
  }

  //fetch GET
  function getBooking() {
    fetch("/api/booking", {
      method: "GET",
      headers: {
        Authorization: `${localStorage.getItem("token")}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data && data.data) {
          // backend
          const date = data.data.date;
          const time = data.data.time;
          const price = data.data.price;
          const attraction = data.data.attraction;
          const id = attraction.id;
          const image = attraction.image;
          const name = attraction.name;
          const address = attraction.address;

          // frontend
          const welcome = document.querySelector(".welcome-title");
          // test.textContent = `${date} ${time} ${price} ${id}${image} ${name} ${address}`;
          const attractionInfo = document.querySelector(".attraction-info");
          attractionInfo.setAttribute("data-id", id);
          const imageElement = document.querySelector(".attraction-image");
          imageElement.src = image;
          const nameElement = document.querySelector(".attraction-name");
          nameElement.textContent = name;
          const addressElement = document.querySelector(".attraction-address");
          addressElement.textContent = address;
          const dateElement = document.querySelector(".attraction-date");
          dateElement.textContent = date;
          const timeElement = document.querySelector(".attraction-time");
          time === "morning"
            ? (timeElement.textContent = "早上 9 點到下午 4 點")
            : (timeElement.textContent = "下午 2 點到晚上 9 點");

          const priceElement = document.querySelector(".attraction-price");
          priceElement.textContent = "新台幣 " + price + " 元";

          // total-price-number queryselector
          const totalPrice = document.querySelector(".total-price-number");
          totalPrice.textContent = "新台幣 " + price + " 元";
        } else {
          //殺光資料

          const attractionInfo = document.querySelector(".attraction-info");
          attractionInfo.innerHTML = "";
          attractionInfo.textContent = "目前沒有任何待預定的行程";
          attractionInfo.style.paddingBottom = "40px";
          attractionInfo.style.marginBottom = "0";
          const userBookingInfo = document.querySelector(".user-booking-info");
          userBookingInfo.style.display = "none";
          const paymentInfo = document.querySelector(".payment-info");
          paymentInfo.style.display = "none";
          const totalPrice = document.querySelector(".total-price-div");
          totalPrice.style.display = "none";

          const separators = [
            ".first-separator",
            ".second-separator",
            ".third-separator",
          ];

          separators.forEach((selector) => {
            const element = document.querySelector(selector);
            if (element) {
              element.style.display = "none";
            }
          });

          document.body.style.backgroundColor = "#757575";
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }

  // fetch DELTE
  const deleteButton = document.querySelector(".delete-attraction");
  deleteButton.addEventListener("click", function () {
    fetch("/api/booking", {
      method: "DELETE",
      headers: {
        Authorization: `${localStorage.getItem("token")}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data && data.ok) {
          window.location.reload();
        }
      })
      .catch((err) => {
        console.log(err);
      });
  });
});

function onSubmit(event) {
  event.preventDefault();

  // 增加表單的驗證
  var form = document.getElementById("user-info-form");
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  // 取得 TapPay Fields 的 status
  const tappayStatus = TPDirect.card.getTappayFieldsStatus();

  // 確認是否可以 getPrime
  if (tappayStatus.canGetPrime === false) {
    alert("can not get prime");
    return;
  }

  // Get prime
  TPDirect.card.getPrime((result) => {
    if (result.status !== 0) {
      alert("get prime error " + result.msg);
      return;
    }
    // alert("get prime 成功，prime: " + result.card.prime);

    // 從畫面中取得使用者的訂單資訊
    const name = document.querySelector("#user-name").value;
    const email = document.querySelector("#user-email").value;
    const phone = document.querySelector("#user-phone").value; // 請確保你的HTML中有此ID
    const priceElement = document.querySelector(".total-price-number");
    const price = priceElement.textContent
      .replace("新台幣 ", "")
      .replace(" 元", "");
    const attractionInfo = document.querySelector(".attraction-info");
    const id = attractionInfo.getAttribute("data-id");
    const attraction_name =
      attractionInfo.querySelector(".attraction-name").textContent;
    const address = attractionInfo.querySelector(
      ".attraction-address"
    ).textContent;
    const image = attractionInfo.querySelector(".attraction-image").src;
    const date = attractionInfo.querySelector(".attraction-date").textContent;

    let time = attractionInfo.querySelector(".attraction-time").textContent;

    if (time === "早上 9 點到下午 4 點") {
      time = "morning";
    } else {
      time = "afternoon";
    }

    // 建立訂單資料
    const orderData = {
      prime: result.card.prime,
      order: {
        price: price,
        trip: {
          attraction: {
            id: id,
            name: attraction_name,
            address: address,
            image: image,
          },
          date: date,
          time: time,
        },
        contact: {
          name: name,
          email: email,
          phone: phone,
        },
      },
    };

    // console.log(orderData);

    // 發送訂單到伺服器
    fetch("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(orderData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.ok) {
          alert("訂單建立成功！");
          window.location.href = "/thankyou?number=" + data.order_number; // 跳轉到感謝頁面
        } else {
          alert("訂單建立失敗: " + data.message);
        }
      })
      .catch((err) => {
        console.error("Error creating order:", err);
      });
  });
}
