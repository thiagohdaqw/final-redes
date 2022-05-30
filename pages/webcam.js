video = document.getElementById('video');
canvas = document.getElementById("canvas-webcam");
canvas2d = canvas.getContext('2d');

webcams = document.getElementById("webcams");

onWebcamCapture = null;

FPS = 6;

navigator.mediaDevices.getUserMedia({video: true})
    .then(mediaStream => {
        video.srcObject = mediaStream;
        video.play();
        captureWebcam();
    })
    .catch(err => {
        console.log('Não há permissões para acessar a webcam')
        console.log(err);
    })

function captureWebcam() {
    setInterval(() => {
        if (onWebcamCapture != null) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas2d.drawImage(video, 0, 0);
            onWebcamCapture(canvas.toDataURL('image/jpeg', 0.1));
            canvas2d.clearRect(0, 0, canvas.width, canvas.height);
        }
    }, 1000/FPS);
}

function createWebcamElement(dataUrl) {
    let img = document.createElement('img');

    img.setAttribute('class', 'webcam');
    webcams.appendChild(img);
    return img;
}

function setImgSrc(img, dataUrl) {
    img.setAttribute('src', dataUrl);
}
