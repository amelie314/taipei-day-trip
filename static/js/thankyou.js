/** @format */

// 假設 response 是後端回傳的訂單編號的回應
let orderNumber = response.order_number;

if (orderNumber) {
  window.location.href = `/thankyou?number=${orderNumber}`;
} else {
  // 處理錯誤或其他情況
}
