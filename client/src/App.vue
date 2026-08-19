<script setup lang="ts">

import { onMounted, ref, reactive, useTemplateRef } from 'vue';

const width = 320; // We will scale the photo width to this
let height = 0; // This will be computed based on the input stream

const photos = reactive([]);
const error = ref('');
const streaming = ref(false);
const videoEl = useTemplateRef('video');
const canvasEl = useTemplateRef('canvas');


onMounted(() => {
    videoEl.value!.addEventListener("canplay", () => {
        if (!streaming.value) {
            videoEl.value!.play();
            height = videoEl.value!.videoHeight / (videoEl.value!.videoWidth / width);
            canvasEl.value!.setAttribute("width", ''+width);
            canvasEl.value!.setAttribute("height", ''+height);
            streaming.value = true;
        }
    });
    clearPhoto();
});


function onCapture(ev: any) {
    ev.preventDefault();
    takePicture();
}


function onAllow() {
    navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((stream) => {
            videoEl.value!.srcObject = stream;
            // videoEl.value.play();
        })
        .catch((err) => {
            if (err.name === 'NotFoundError') {
                videoEl.value!.src = './sample.mp4';
                videoEl.value!.muted = true;
                // videoEl.value.play();
                return;
            }
            console.error('Failed to enable video:', err);
            error.value = 'Failed to enable video: ' + err;
        });
}


function hasGetUserMedia(): boolean {
    return !!navigator?.mediaDevices?.getUserMedia;
}


function clearPhoto() {
    const context = canvasEl.value!.getContext("2d");
    if (context) {
        context.fillStyle = "#aaaaaa";
        context.fillRect(0, 0, canvasEl.value!.width, canvasEl.value!.height);
    }
    photos.length = 0;
}

function takePicture() {
    const context = canvasEl.value!.getContext("2d");
    if (context && width && height && videoEl.value) {
        canvasEl.value!.width = width;
        canvasEl.value!.height = height;
        context.filter = 'none';
        context.drawImage(videoEl.value, 0, 0, width, height);

        const data = canvasEl.value!.toDataURL("image/png");
        uploadPhoto(data);
    } else {
        clearPhoto();
    }
}


// async function onUploadPhotos() {
//     const form = new FormData();
//     for (let photo of photos) {
//         const blob = await (await fetch(photo)).blob();
//         form.append('files', new File([blob], 'photo.png'));
//     }
//     const response = await fetch(
//         'http://192.168.100.119:8000/upload',
//         {
//             method: 'POST',
//             body: form,
//         },
//     );
//     clearPhoto();
// }


function getServerUploadUrl(): string {
    if (import.meta.env.MODE === 'development') {
        return 'http://localhost:8000/upload';
    }
    return './api/upload';
}


async function uploadPhoto(dataURL: string)
{
    try {
        const form = new FormData();
        const blob = await (await fetch(dataURL)).blob();
        form.append('files', new File([blob], 'photo.png'));
        await fetch(
            getServerUploadUrl(),
            {
                method: 'POST',
                body: form,
            },
        );
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
        <div v-if="streaming" class="capture-button-area">
            <button @click="onCapture">
            </button>
        </div>

        <div v-if="!streaming" class="allow-button-area">
            <button @click="onAllow">
                Allow camera
            </button>
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
    font-size: smaller;
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    height: 1.5em;
    display: flex;
    align-items: center;
    margin: 0;
    padding: 0.5em;
    justify-content: center;
    background: darkred;
    color: white;
    font-weight: bold;
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
    background: radial-gradient(circle at center, lightgray 0, darkgray 100%);
    outline: solid 2px lightgray;
    color: inherit;
    transition: transform 200ms;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.75);
    border: solid 2px #777;
    transform: scale(1);
}

.capture-button-area button:active {
    transition: transform 0ms;
    transform: scale(0.92);
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

.allow-button-area {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.allow-button-area button {
    padding: 1em;
}

</style>
