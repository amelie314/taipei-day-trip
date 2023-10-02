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
  });

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
        console.log(data);
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

          const firstSeparetor = document.querySelector(".first-separator");
          const secondSeparetor = document.querySelector(".second-separator");
          const thirdSeparetor = document.querySelector(".third-separator");
          firstSeparetor.style.display = "none";
          secondSeparetor.style.display = "none";
          thirdSeparetor.style.display = "none";

          document.body.style.backgroundColor = "#757575";
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }

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
        console.log(data);
        if (data && data.ok) {
          window.location.reload();
        }
      })
      .catch((err) => {
        console.log(err);
      });
  });

  // fetch DELTE
});
