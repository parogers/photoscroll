<script setup lang="ts">

import {
    onMounted,
    ref,
    useTemplateRef,
    nextTick,
} from 'vue';


const MAX_FRAME_WIDTH = 160;
const AUTO_ROTATE = false;


const version = ref<string>(import.meta.env.APP_VERSION);
const error = ref('');
const streaming = ref(false);
const videoEl = useTemplateRef('video');
const canvasEl = useTemplateRef('canvas');
const facingUser = ref(true);
const flipX = ref(true);
const capturing = ref(false);
const capturePreview = ref('');
const capturePreviewHidden = ref(true);


onMounted(async () => {
    await onAllow();
})


function onCanPlay() {
    if (!streaming.value) {
        streaming.value = true;
    }
}


function onVideoError(err: any) {
    error.value = 'Video error: ' + err;
    console.error('Video error:', err);
}


function onVideoEnded() {
    streaming.value = false;
    capturing.value = false;
    videoEl.value!.srcObject = null;
}


async function onCapture(ev: any) {
    ev?.preventDefault();
    capturing.value = true;
    await nextTick();
    const imageURL = await takePicture();
    capturing.value = false;
    await nextTick();
    if (imageURL) {
        capturePreview.value = imageURL;
        capturePreviewHidden.value = false;
        clearTimeout(dismissCapturePreview);
        await nextTick();
        await uploadPhoto(imageURL);
        setTimeout(dismissCapturePreview, 1500);
    }
}


async function dismissCapturePreview() {
    capturePreviewHidden.value = true;
    await nextTick();
}


function onToggleFacing() {
    facingUser.value = !facingUser.value;
    onAllow();
}


async function onAllow() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: facingUser.value ? 'user' : 'environment',
            },
            audio: false,
        });
        const streams = stream.getVideoTracks();
        if (streams.length) {
            const constraints = streams[0].getConstraints();
            flipX.value = constraints.facingMode === 'user';
        } else {
            flipX.value = false;
        }
        videoEl.value!.srcObject = stream;
        videoEl.value!.play();
        error.value = '';

    } catch(err: any) {
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
    }
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
    const rotated = AUTO_ROTATE && width > height;
    const scaleX = (flipX.value ? -1 : 1);
    const [canvasWidth, canvasHeight] = rotated ? [height, width] : [width, height];

    canvasEl.value.width = canvasWidth;
    canvasEl.value.height = canvasHeight;
    context.filter = 'grayscale(1)';

    if (rotated) {
        context.translate(height, 0);
        context.rotate(Math.PI/2);
    }
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
            :class="{ flipx: flipX, capturing: capturing }"
            @canplay="onCanPlay"
            @error="onVideoError"
            @ended="onVideoEnded"
        >
            Video stream not available
        </video>

        <img
            v-if="capturePreview"
            class="capture-preview"
            :class="{ hidden: capturePreviewHidden }"
            :src="capturePreview"
        >

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
    font-size: larger;
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
    left: 0.5em;
    color: gray;
}

.capture-preview {
    background: white;
    position: absolute;
    right: 0.5em;
    bottom: 0.5em;
    width: 6em;
    height: auto;
    border-radius: 1em;
    border: solid 2px white;
    opacity: 1;
    transition: opacity 100ms 250ms;
}

.capture-preview.hidden {
    opacity: 0;
    transition: opacity 750ms 250ms;
}
</style>
