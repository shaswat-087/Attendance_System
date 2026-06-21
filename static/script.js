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
    .then(async res => {
        if (!res.ok) {
            throw new Error("Server returned " + res.status);
        }
        return res.json();
    })
    .then(data => {
        // 1. Update the main status box with the Flask 'message'
        statusBox.innerHTML = data.message;
        const infoBox = document.querySelector(".info");

        // 2. Check if the 'name' key exists in the JSON payload
        if (data.name) {
            statusBox.className = "status success";
            videoBox.style.boxShadow = "0 0 20px #0ff";
            
            // 3. Inject matching variables directly from the Flask payload
            infoBox.innerHTML = `
                <p><span>Name: <strong>${data.name}</strong></span></p>
                <p><span>Year: <strong>${data.class}</strong></span></p>
                <p><span>Section: <strong>${data.section}</strong></span></p>
                <p><span>Roll Number: <strong>${data.roll}</strong></span></p>
                <p><span>Match Confidence: <strong>${data.percentage}%</strong></span></p>
            `;
        } else {
            // Handle cases where no face was found or not recognized
            statusBox.className = "status error";
            videoBox.style.boxShadow = "0 0 20px #ff0000";
            infoBox.innerHTML = ""; // Clear old data
        }
    })
    .catch(err => {
        console.error("Fetch Error:", err);
        statusBox.innerHTML = "❌ Error connecting to server";
        statusBox.className = "status error";
        document.querySelector(".info").innerHTML = ""; 
    });
})
