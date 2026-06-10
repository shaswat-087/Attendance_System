// SELECT ELEMENTS
const video = document.querySelector("video");
const captureBtn = document.querySelector(".capture");
const statusBox = document.querySelector(".status");
const videoBox = document.querySelector(".video-section");

// START CAMERA
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        statusBox.innerHTML = "Camera access denied ❌";
    });

// CAPTURE BUTTON CLICK
captureBtn.addEventListener("click", () => {

    // 👉 1. Change status to processing
    statusBox.innerHTML = "🔍 Scanning face...";
    statusBox.className = "status processing";

    // 👉 2. Add glow effect to video
    videoBox.style.boxShadow = "0 0 30px #00eaff, 0 0 80px #00eaff inset";

    // 👉 3. Capture frame from video
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL("image/png");

    console.log("Captured Image:", imageData);

    // 👉 4. Send captured frame to Flask backend
    fetch("/recognize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        statusBox.innerHTML = data.message;
        statusBox.className = "status success";
        videoBox.style.boxShadow = "0 0 20px #0ff";
    })
    .catch(err => {
        statusBox.innerHTML = "❌ Error connecting to server";
        statusBox.className = "status error";
    });
});
