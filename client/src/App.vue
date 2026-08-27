<script setup lang="ts">

import {
    onMounted,
    ref,
    useTemplateRef,
    nextTick,
} from 'vue';


const MAX_FRAME_WIDTH = 160;


const version = ref<string>(import.meta.env.APP_VERSION);
const error = ref('');
const streaming = ref(false);
const videoEl = useTemplateRef('video');
const canvasEl = useTemplateRef('canvas');
const facingUser = ref(true);
const flipX = ref(true);
const capturing = ref(false);


onMounted(() => {
    videoEl.value!.addEventListener("canplay", () => {
        if (!streaming.value) {
            streaming.value = true;
        }
    });
});


async function onCapture(ev: any) {
    ev.preventDefault();
    capturing.value = true;
    await nextTick();
    const imageURL = await takePicture();
    capturing.value = false;
    await nextTick();
    if (imageURL) {
        await uploadPhoto(imageURL);
    }
}


function onToggleFacing() {
    facingUser.value = !facingUser.value;
    onAllow();
}


function onAllow() {
    navigator.mediaDevices
        .getUserMedia({
            video: {
                facingMode: facingUser.value ? 'user' : 'environment',
            },
            audio: false,
         })
        .then((stream) => {
            const streams = stream.getVideoTracks();
            if (streams.length) {
                const constraints = streams[0].getConstraints();
                flipX.value = constraints.facingMode === 'user';
            } else {
                flipX.value = false;
            }
            videoEl.value!.srcObject = stream;
            videoEl.value!.play();
        })
        .catch((err) => {
            if (err.name === 'NotFoundError' && isModeDevelopment()) {
                // Fallback for testing
                videoEl.value!.src = './sample.mp4';
                videoEl.value!.muted = true;
                videoEl.value!.play();
                return;
            }
            console.error('Failed to enable video:', err);
            if (err.name === 'NotFoundError') {
                error.value = 'Camera not found';
            } else {
                error.value = 'Failed to enable video: ' + err;
            }
        });
}


function hasGetUserMedia(): boolean {
    return !!navigator?.mediaDevices?.getUserMedia;
}


function getMaxFit(width: number, height: number): {
    width: number,
    height: number,
} {
    const scale = MAX_FRAME_WIDTH/width;
    return {
        width: MAX_FRAME_WIDTH,
        height: Math.round(height*scale)|0,
    };
}


async function takePicture(): Promise<string> {
    if (
        !videoEl.value ||
        !canvasEl.value ||
        !videoEl.value.videoWidth ||
        !videoEl.value.videoHeight
    ) {
        return '';
    }
    const { width, height } = getMaxFit(
        videoEl.value.videoWidth,
        videoEl.value.videoHeight,
    );
    const context = canvasEl.value.getContext("2d");
    if (!context) {
        return '';
    }
    const scaleX = flipX.value ? -1 : 1;
    canvasEl.value.width = width;
    canvasEl.value.height = height;
    context.filter = 'grayscale(1)';
    context.scale(scaleX, 1);
    context.drawImage(videoEl.value, 0, 0, scaleX*width, height);
    const data = canvasEl.value!.toDataURL("image/png");
    return data;
}


function isModeDevelopment(): boolean {
    return import.meta.env.MODE === 'development';
}


function getServerUploadUrl(): string {
    if (isModeDevelopment()) {
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
        <video
            ref="video"
            :class="{ flipx: flipX, capturing: capturing }">
            Video stream not available
        </video>
        <div v-if="streaming" class="capture-button-area">
            <div></div>

            <button @click="onCapture" class="capture">
            </button>

            <button @click="onToggleFacing" class="flip">
                &hookleftarrow;
            </button>
        </div>

        <div v-if="!streaming" class="allow-button-area">
            <button @click="onAllow">
                Allow camera
            </button>
        </div>

        <div class="version">
            v{{ version }}
        </div>
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
    display: block;
    width: 100%;
    height: auto;
    max-height: 100%;
}

video.flipx {
    transform: scaleX(-1);
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
    display: flex;
    height: 100dvh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: black;
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
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1em;
}

.capture-button-area button.capture {
    position: relative;
    width: 3em;
    height: 3em;
    border-radius: 100%;
    background: radial-gradient(circle at center, white 0, lightgray 100%);
    outline: solid 2px lightgray;
    color: inherit;
    transition: transform 200ms;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.75);
    border: solid 2px #777;
    transform: scale(1);
    font-size: x-large;
}

.capture-button-area button.capture:active {
    transition: transform 0ms;
    transform: scale(0.92);
    box-shadow: none;
}

.capture-button-area button.capture::before {
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
    pointer-events: none;
}


.capture-button-area button.capture:active::before {
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

.capture-button-area div, .capture-button-area .flip {
    width: 2em;
}

button.flip {
    aspect-ratio: 1;
    border-radius: 100%;
    border: none;
    padding: 0;
    margin: 0;
    background: lightgray;
    font-size: larger;
    /* color: inherit; */
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.75);
}

button.flip:active {
    background: #eee;
    transform: scale(0.95);
    box-shadow: none;
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

video {
    opacity: 1;
    transition: opacity 200ms;
}

video.capturing {
    opacity: 0.25;
    transition: opacity 0s;
}

.version {
    position: absolute;
    bottom: 0.25em;
    right: 0.25em;
    color: gray;
}
</style>
