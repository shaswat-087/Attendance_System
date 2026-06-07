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

    // 👉 4. Simulate processing (later backend)
    setTimeout(() => {

        // ✅ SUCCESS CASE (for demo)
        statusBox.innerHTML = "✅ Attendance Marked!";
        statusBox.className = "status success";

        // 👉 Remove glow
        videoBox.style.boxShadow = "0 0 20px #0ff";

    }, 2500);

});


// FILE UPLOAD SUPPORT
const uploadInput = document.querySelector(".upload-section");

uploadInput.addEventListener("change", () => {

    if (uploadInput.files.length > 0) {

        statusBox.innerHTML = "📂 Image uploaded, processing...";
        statusBox.className = "status processing";

        setTimeout(() => {
            statusBox.innerHTML = "✅ Attendance Marked via Upload!";
            statusBox.className = "status success";
        }, 2000);
    }

});
