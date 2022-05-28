video = document.querySelector('#video');
img = document.querySelector("#img");
canvas = document.querySelector("#canvas");
canvas2d = canvas.getContext('2d');

WIDTH = 400;
HEIGHT = 300;
FPS = 6;

navigator.mediaDevices.getUserMedia({video: true})
    .then(mediaStream => {
        video.srcObject = mediaStream;
        video.play();
        addInterval();
    })
    .catch(err => {
        console.log('Não há permissões para acessar a webcam')
        console.log(err);
    })

function addInterval() {
    setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas2d.drawImage(video, 0, 0);
        renderBlob(canvas.toDataURL('image/jpeg', 0.1));
    }, 1000/FPS);
}

function renderBlob(dataURL) {
    console.log(dataURL.length);
    img.setAttribute('src', dataURL);
}