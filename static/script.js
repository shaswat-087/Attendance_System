// SELECT ELEMENTS
const video = document.querySelector("video");
const captureBtn = document.querySelector(".capture");
const statusBox = document.querySelector(".status");
const videoBox = document.querySelector(".video-section");

// START CAMERA
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
    video.play(); // ensure playback starts
  })
  .catch(err => {
    statusBox.innerHTML = "Camera access denied ❌";
  });

// CAPTURE BUTTON CLICK
captureBtn.addEventListener("click", () => {
  statusBox.innerHTML = "🔍 Scanning face...";
  statusBox.className = "status processing";
  videoBox.style.boxShadow = "0 0 30px #00eaff, 0 0 80px #00eaff inset";

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);

  const imageData = canvas.toDataURL("image/png");

  fetch("/recognize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData })
  })
  .then(res => res.json())
  .then(data => {
    statusBox.innerHTML = data.message;
    const infoBox = document.querySelector(".info");

    if (data.name) {
      statusBox.className = "status success";
      videoBox.style.boxShadow = "0 0 20px #0ff";
      infoBox.innerHTML = `
        <p>Name: <strong>${data.name}</strong></p>
        <p>Year: <strong>${data.class}</strong></p>
        <p>Section: <strong>${data.section}</strong></p>
        <p>Roll Number: <strong>${data.roll}</strong></p>
        <p>Match Confidence: <strong>${data.percentage}%</strong></p>
      `;
    } else {
      statusBox.className = "status error";
      videoBox.style.boxShadow = "0 0 20px #ff0000";
      infoBox.innerHTML = "";
    }
  })
  .catch(err => {
    console.error("Fetch Error:", err);
    statusBox.innerHTML = "❌ Error connecting to server";
    statusBox.className = "status error";
    document.querySelector(".info").innerHTML = "";
  });
});
