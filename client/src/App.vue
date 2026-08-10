<script setup lang="ts">

import { onMounted, ref, reactive, useTemplateRef } from 'vue';

const width = 320; // We will scale the photo width to this
let height = 0; // This will be computed based on the input stream

let streaming = false;

const photos = reactive([]);
const error = ref('');
const videoEl = useTemplateRef('video');
const photoEl = useTemplateRef('photo');
const canvasEl = useTemplateRef('canvas');


onMounted(() => {
    const startButton = document.getElementById("start-button");
    const allowButton = document.getElementById("permissions-button");
    videoEl.value.addEventListener("canplay", (ev) => {
        if (!streaming) {
            height = videoEl.value.videoHeight / (videoEl.value.videoWidth / width);

            videoEl.value.setAttribute("width", width);
            videoEl.value.setAttribute("height", height);
            canvasEl.value.setAttribute("width", width);
            canvasEl.value.setAttribute("height", height);
            streaming = true;
        }
    });
    clearPhoto();
});


function onCapture(ev) {
    ev.preventDefault();
    takePicture();
}


function onClear(ev) {
    ev.preventDefault();
    clearPhoto();
}


function onAllow() {
    navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
            videoEl.value.srcObject = stream;
            videoEl.value.play();
        })
        .catch((err) => {
            if (err.name === 'NotFoundError') {
                videoEl.value.src = '/sample.mp4';
                videoEl.value.muted = true;
                videoEl.value.play();
                return;
            }
            console.error('An error occurred:', err);
            error.value = err;
        });
}


function hasGetUserMedia(): boolean {
    return !!navigator?.mediaDevices?.getUserMedia;
}


function clearPhoto() {
    const context = canvasEl.value.getContext("2d");
    context.fillStyle = "#aaaaaa";
    context.fillRect(0, 0, canvasEl.value.width, canvasEl.value.height);

    // const data = canvasEl.value.toDataURL("image/png");
    // photoEl.value.setAttribute("src", data);
    photos.length = 0;
}

function takePicture() {
    const context = canvasEl.value.getContext("2d");
    if (width && height) {
        canvasEl.value.width = width;
        canvasEl.value.height = height;
        context.filter = 'none';
        context.drawImage(videoEl.value, 0, 0, width, height);

        const data = canvasEl.value.toDataURL("image/png");
        photos.push(data);
        // photoEl.value.setAttribute("src", data);
    } else {
        clearPhoto();
    }
}
</script>

<template>
    <p v-if="error" class="error">{{ error }}</p>

    <p v-if="!hasGetUserMedia()" class="error">
        Media devices API not supported
    </p>

    <div>
        <button id="permissions-button" @click="onAllow">
            Allow camera
        </button>
    </div>

    <video ref="video">Video stream not available.</video>
    <div>
        <button id="start-button" @click="onCapture">
            Capture photo
        </button>

        <button @click="onClear">
            Clear
        </button>
    </div>

    <div>
        <img v-for="photo of photos" ref="photo" :src="photo" />
    </div>

    <canvas ref="canvas"></canvas>
</template>

<style scoped>
video, figure {
    border: solid 1px gray;
}

button {
    font-size: x-large;
}

.error {
    color: red;
}

canvas {
    display: none;
}

figure {
    margin: 0;
    padding: 0;
    margin-top: 1em;
}

img {
    width: 10em;
    height: auto;
}
</style>
