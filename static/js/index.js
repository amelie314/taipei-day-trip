/** @format */
//ubuntu server IP & PORT
//let RemoteURL = `http://3.131.18.21:3000/`; //上傳時用
// let LocalURL = `http://127.0.0.1:3000/`; // 開發時用

let isLoading = false;
let keywordInput = "";
let nextPage = 0;

fetchData(nextPage);

function fetchData(page, keyword = "") {
  // 如果正在載入或沒有下一頁，則返回
  if (isLoading || nextPage === null) return;
  // 設置 isLoading 為 true，防止重複載入
  isLoading = true;

  // console.log(
  //   "loading API ?page=",
  //   page,
  //   "?keyword=",
  //   keyword ? keyword : "全部"
  // );

  let apiUrl = `/api/attractions?page=${page}`;
  // let apiUrl = `${RemoteURL}api/attractions?page=${page}`;
  if (keyword) {
    apiUrl += `&keyword=${keyword}`;
  }
  // console.log(apiUrl);

  // 載入資料
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      if (data.data && data.data.length > 0) {
        if (keyword && nextPage === 0) {
          const profile = document.querySelector(".profile");
          profile.innerHTML = ""; // 清空原本的內容
        }

        createElements(data);

        nextPage = data.nextPage;

        // console.log("Next loading API ?page=", nextPage);
      } else {
        // 如果沒有找到相關資料，你也可以選擇顯示一個提示訊息
        const profile = document.querySelector(".profile");
        profile.innerHTML = keyword ? "未找到相關景點" : "";
      }

      isLoading = false; // 設置 isLoading 為 false，以允許下一次載入
    })
    .catch((error) => {
      console.error("從 API 獲取資料時發生錯誤：", error);
      isLoading = false; // 設置 isLoading 為 false，以允許下一次載入
    });
}

// 監聽滾動事件
window.addEventListener("scroll", () => {
  if (isLoading) return;

  const { bottom } = document
    .querySelector(".container")
    .getBoundingClientRect();
  const windowHeight = window.innerHeight;

  if (bottom <= windowHeight + 10) {
    fetchData(nextPage, keywordInput);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  //Arrow Button
  const listContainer = document.querySelector(".list-container");
  const prevButton = document.querySelector(".prev-button");
  const nextButton = document.querySelector(".next-button");
  const scrollAmount = 150; // 你可以根據需要調整這個數值

  prevButton.addEventListener("click", () => {
    listContainer.scrollLeft -= scrollAmount;
  });

  nextButton.addEventListener("click", () => {
    listContainer.scrollLeft += scrollAmount;
  });

  // 搜尋功能
  document
    .getElementById("search-button")
    .addEventListener("click", function () {
      const keywordValue = document.getElementById("search-input").value;
      if (keywordValue) {
        // 確保關鍵字不是空的

        nextPage = 0;

        keywordInput = keywordValue;

        fetchData(nextPage, keywordInput);
      }
    });
});

// function setCurrentIndex(index) {
//   currentIndex = index;
//   updateListPosition();
// }
// function updateListPosition() {
//   const itemWidth = listItems[0].offsetWidth;
//   const newPosition = -currentIndex * itemWidth;
//   listContainer.style.transform = `translateX(${newPosition}px)`;
// }

// mrt buttons contents
function fetchAndGenerateOptions() {
  // console.log("triggered!");

  // fetch(`${RemoteURL}api/mrts`)
  fetch(`/api/mrts`)
    .then((response) => response.json())
    .then((data) => {
      const optionsNull = data.data;
      const options = optionsNull.filter((optionsNull) => optionsNull !== null);
      const listContainer = document.querySelector(".list-container");
      listContainer.innerHTML = "";

      options.forEach((option) => {
        const listItem = document.createElement("button");
        listItem.className = `list-item`;
        listItem.textContent = option;
        listItem.style.color = "#666";

        listItem.addEventListener("click", function () {
          const searchInput = document.getElementById("search-input");
          searchInput.value = option;

          nextPage = 0;

          keywordInput = option;

          fetchData(nextPage, option); // 觸發搜尋
        });

        listContainer.appendChild(listItem);
      });
    })
    .catch((error) => {
      console.error("從 API 獲取資料時發生錯誤：", error);
    });
}

fetchAndGenerateOptions();

function createElements(data) {
  const attractions = data["data"];
  const profile = document.querySelector(".profile");

  for (let i = 0; i < attractions.length; i++) {
    let liProfile = document.createElement("li");
    liProfile.className = `profile-li profile-li-${i + 1}`;

    // 為每個 li 添加點擊事件
    liProfile.addEventListener("click", function () {
      // window.location = `${RemoteURL}attraction/${attractions[i].id}`;
      window.location = `attraction/${attractions[i].id}`;
    });

    let divCardTop = document.createElement("div");
    divCardTop.className = "card-top";
    let divCardBottom = document.createElement("div");
    divCardBottom.className = "card-bottom";

    let imgElement = document.createElement("img");
    imgElement.src = attractions[i].images[0] || "";
    imgElement.alt = `profile-img-${i + 1}`;
    imgElement.className = "main-img";

    imgElement.onerror = function () {
      this.onerror = null; // 避免無窮迴圈
      this.alt = "目前無圖片可顯示";
      this.style.textAlign = "center";
      this.style.lineHeight = this.height + "px"; // 設置行高使文字垂直置中
      this.style.fontWeight = "bold";
      this.style.color = "#666";
    };

    let divElementTitle = document.createElement("div");
    divElementTitle.className = `profile-title profile-title-${i + 1}`;
    let spanElement = document.createElement("span");
    spanElement.textContent = attractions[i].name;

    let divElementCategory = document.createElement("div");
    divElementCategory.className = `profile-category profile-category-${i + 1}`;
    divElementCategory.textContent = attractions[i].category;

    let divElementMRT = document.createElement("div");
    divElementMRT.className = `profile-mrt profile-mrt-${i + 1}`;
    divElementMRT.textContent = attractions[i].mrt;

    liProfile.appendChild(divCardTop);
    divCardTop.appendChild(imgElement);
    divCardTop.appendChild(divElementTitle);
    divElementTitle.appendChild(spanElement);

    liProfile.appendChild(divCardBottom);
    divCardBottom.appendChild(divElementCategory);
    divCardBottom.appendChild(divElementMRT);
    profile.appendChild(liProfile);
  }
}
