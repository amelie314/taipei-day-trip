/** @format */
//ubuntu server IP & PORT
//let RemoteURL = `http://3.131.18.21:3000/`; //上傳時用
// let LocalURL = `http://127.0.0.1:3000/`; // 開發時用

document.addEventListener("DOMContentLoaded", function () {
  const logoElement = document.querySelector(".logo");

  // 為這個 h1 元素添加 click 事件監聽器
  logoElement.addEventListener("click", function () {
    // window.location = RemoteURL;
    window.location = "/";
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  const lastSegment = path.split("/").pop();
  let currentImageIndex = 0;
  let images;

  function showImage(index) {
    const imageSlider = document.getElementById("image-slider");
    const indicators = document.querySelectorAll(".indicator");
    imageSlider.children[currentImageIndex].classList.remove("active");
    indicators[currentImageIndex].classList.remove("active");
    currentImageIndex = index;
    imageSlider.children[currentImageIndex].classList.add("active");
    indicators[currentImageIndex].classList.add("active");
  }

  // fetch(`${RemoteURL}api/attraction/${lastSegment}`)
  fetch(`/api/attraction/${lastSegment}`)
    .then((response) => response.json())
    .then((data) => {
      if (data && data.data) {
        const { name, mrt, category, images: fetchedImages } = data.data;
        images = fetchedImages;

        const mainContent = document.getElementById("main-content");
        const bookingInfo = document.getElementById("booking-info");

        let imageHTML = "";
        images.forEach((img, index) => {
          imageHTML += `<img src="${img}" alt="${name}" class="${
            index === 0 ? "active" : ""
          }">`;
        });

        const imageSlider = document.getElementById("image-slider");
        const indicatorsElement = document.getElementById("indicators");
        let indicatorsHTML = "";
        // 新增的小圈圈指示 HTML

        images.forEach((img, index) => {
          indicatorsHTML += `<span class="indicator ${
            index === 0 ? "active" : ""
          }"></span>`;
        });
        imageSlider.innerHTML = imageHTML;
        indicatorsElement.innerHTML = indicatorsHTML;

        bookingInfo.innerHTML = `
                            <div id="combined-content">
                                <h1>${name}</h1>
                                <p>${category} at ${mrt}</p>
                                <form>
                                    <h4 class="p-bold">訂購導覽行程</h4>
                                    <p>以此景點為中心的一日行程，帶您探索城市角落故事</p>
                                    <label for="photo-date">選擇日期：</label>
                                    <input type="date" id="photo-date" class="photo-date" placeholder="yyyy/mm/dd">
                                    <br>
                                    <label>選擇時間：</label>
                                    <input type="radio" id="morning" name="photo-radio" value="上半天" checked>
                                    <label for="morning">上半天</label>
                                    <input type="radio" id="afternoon" name="photo-radio" value="下半天">
                                    <label for="afternoon">下半天</label>
                                    <br>
                                    <label for="fee">費用：<span id="fee" name="fee-radio" class="fee">新台幣 2000 元</span></label>
                                    <br>
                                    <button type="submit">開始預約行程</button>
                                </form>
                            </div>
                        `;
        const additionalInfo = document.getElementById("additional-info");
        const { address, description, transport } = data.data;
        let truncatedDescription = description;
        let isTruncated = false;
        let isExpanded = false; // 用來追蹤目前是否已經展開

        function updateDescription() {
          if (isExpanded) {
            document.getElementById("descriptionPara").innerHTML =
              description +
              ' <button class="more-indicator" id="moreIndicator" style="cursor:pointer;">{顯示更少}</button>';
          } else {
            document.getElementById("descriptionPara").innerHTML =
              truncatedDescription;
          }

          // 更新點擊事件
          document
            .getElementById("moreIndicator")
            .addEventListener("click", function () {
              isExpanded = !isExpanded;
              updateDescription();
            });
        }

        // 檢查描述是否需要被截斷
        if (description.length > 420) {
          truncatedDescription =
            description.substring(0, 420) +
            ' <button class="more-indicator" id="moreIndicator" style="cursor:pointer;">{...}</button>';
          isTruncated = true;
        } else {
          truncatedDescription = description;
        }

        // 將處理後的描述和其他資料插入到 HTML 中
        additionalInfo.innerHTML = `<p class="info" id="descriptionPara">${truncatedDescription}</p>
    <h3 class="info-title">景點地址：</h3>
    <p class="info">${address}</p>
    <h3 class="info-title">交通方式：</h3>
    <p class="info">${transport}</p>
  `;

        // 如果描述被截斷，添加點擊事件以展開/收起完整描述
        if (isTruncated) {
          updateDescription();
        }

        // 費用切換程式碼
        const feeElement = document.getElementById("fee");
        const morningRadio = document.getElementById("morning");
        const afternoonRadio = document.getElementById("afternoon");

        morningRadio.addEventListener("change", function () {
          feeElement.textContent = "新台幣 2000 元";
        });

        afternoonRadio.addEventListener("change", function () {
          feeElement.textContent = "新台幣 2500 元";
        });

        showImage(0);

        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");

        prevBtn.addEventListener("click", function () {
          let prevIndex =
            (currentImageIndex - 1 + images.length) % images.length;
          showImage(prevIndex);
        });

        nextBtn.addEventListener("click", function () {
          let nextIndex = (currentImageIndex + 1) % images.length;
          showImage(nextIndex);
        });
      }
    })
    .catch((error) => {
      console.error("發生錯誤：", error);
    });
});
