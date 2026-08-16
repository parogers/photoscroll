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
    videoEl.value.addEventListener("canplay", (ev) => {
        if (!streaming) {
            height = videoEl.value.videoHeight / (videoEl.value.videoWidth / width);
            canvasEl.value.setAttribute("width", width);
            canvasEl.value.setAttribute("height", height);
            streaming = true;
        }
    });
    onAllow();
    clearPhoto();
});


function onCapture(ev) {
    console.log('capture');
    return;
    ev.preventDefault();
    takePicture();
}


function onClear(ev) {
    ev.preventDefault();
    clearPhoto();
}


function onAllow() {
    videoEl.value.src = '/sample.mp4';
    videoEl.value.muted = true;
    videoEl.value.play();
    return;

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

        canvasEl.value.toBlob(blob => {
            console.log(blob);
            uploadPhoto(blob);
        })

        // uploadPhoto(data);
    } else {
        clearPhoto();
    }
}


async function uploadPhoto(data)
{
    try {
        const form = new FormData();
        form.append('file', new File([data], 'photo.png'));
        const response = await fetch(
            'http://192.168.100.119:8000/upload',
            {
                method: 'POST',
                body: form,
            },
        );
        console.log(response);
    } catch(error) {
        alert(error);
    }
}
</script>

<template>
    <p v-if="error" class="error">{{ error }}</p>

    <p v-if="!hasGetUserMedia()" class="error">
        Media devices API not supported
    </p>

    <div class="video-area">
        <video ref="video">Video stream not available.</video>
        <div class="capture-button-area">
            <button @click="onCapture">
            </button>
            <!-- <button id="permissions-button" @click="onAllow">
                Allow camera
            </button> -->
        </div>
    </div>

    <div>
        <img v-for="photo of photos" ref="photo" :src="photo" />
    </div>

    <canvas ref="canvas"></canvas>
</template>

<style scoped>
body {
    background: white;
}

figure {
    border: solid 1px gray;
}

video {
    width: 100%;
    height: auto;
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

.video-area {
    height: 100dvh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: lightgray;
    overflow: hidden;
}

.capture-button-area {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 1.25em;
    text-align: center;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.25) 50%, rgba(0, 0, 0, 0) 100%);
}

.capture-button-area button {
    position: relative;
    width: 3em;
    height: 3em;
    border-radius: 100%;
    /* background: lightgray; */
    background: radial-gradient(circle at center, lightgray 0, darkgray 100%);
    outline: solid 2px lightgray;
    color: inherit;
    transition: background-color 250ms, outline-color 250ms;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.75);
    border: solid 2px #777;
}

.capture-button-area button:active {
    /* background: white; */
    /* outline-color: gray; */
    transition: background-color 0ms;
    transform: scale(0.95);
    box-shadow: none;
}

.capture-button-area button::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(255, 255, 255, 0);
    border-radius: 100%;
    transform: scale(3);
    transition: transform 250ms, background-color 250ms;
}


.capture-button-area button:active::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(255, 255, 255, 0.25);
    border-radius: 100%;
    transform: scale(1);
    transition: transform 0ms;
}

</style>
