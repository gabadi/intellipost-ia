<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import {
    createCameraService,
    isCameraSupported,
    getCameraErrorMessage,
  } from '../../utils/camera';
  import type { CameraCapture } from '../../types/product';

  export let onPhotoCapture: (file: File) => void;
  export let onClose: () => void;
  export let maxPhotos = 8;
  export let capturedCount = 0;

  let videoElement: HTMLVideoElement;
  const cameraService = createCameraService();
  let cameraState: CameraCapture = {
    stream: null,
    isActive: false,
    permissionStatus: 'prompt',
    error: null,
  };

  let isCapturing = false;
  let lastCapturedPhoto: string | null = null;
  let showPreview = false;
  let previewFile: File | null = null;

  onMount(async () => {
    if (!isCameraSupported()) {
      cameraState.error = 'Camera is not supported by your browser';
      return;
    }

    await initializeCamera();
  });

  onDestroy(() => {
    cleanup();
  });

  async function initializeCamera() {
    try {
      cameraState = await cameraService.requestCameraPermission();

      if (cameraState.stream && videoElement) {
        await cameraService.startVideoPreview(videoElement);
      }
    } catch (error) {
      cameraState.error = getCameraErrorMessage(error as Error);
    }
  }

  async function capturePhoto() {
    if (!cameraState.isActive || isCapturing) return;

    try {
      isCapturing = true;
      const file = await cameraService.capturePhoto();

      // Show preview
      previewFile = file;
      lastCapturedPhoto = URL.createObjectURL(file);
      showPreview = true;
    } catch (error) {
      cameraState.error = getCameraErrorMessage(error as Error);
    } finally {
      isCapturing = false;
    }
  }

  function acceptPhoto() {
    if (previewFile) {
      onPhotoCapture(previewFile);
      resetPreview();
    }
  }

  function retakePhoto() {
    resetPreview();
  }

  function resetPreview() {
    showPreview = false;
    if (lastCapturedPhoto) {
      URL.revokeObjectURL(lastCapturedPhoto);
      lastCapturedPhoto = null;
    }
    previewFile = null;
  }

  async function switchCamera() {
    try {
      await cameraService.switchCamera();
      if (videoElement) {
        await cameraService.startVideoPreview(videoElement);
      }
    } catch (error) {
      cameraState.error = getCameraErrorMessage(error as Error);
    }
  }

  async function cleanup() {
    await cameraService.stopCamera();
    if (lastCapturedPhoto) {
      URL.revokeObjectURL(lastCapturedPhoto);
    }
  }

  function handleClose() {
    cleanup();
    onClose();
  }

  $: canCaptureMore = capturedCount < maxPhotos;
  $: remainingPhotos = maxPhotos - capturedCount;
</script>

<div class="camera-modal">
  <div class="camera-container">
    <header class="camera-header">
      <button class="close-btn" on:click={handleClose} aria-label="Close camera"> ✕ </button>
      <h2 class="camera-title">Take Photo</h2>
      <div class="photo-counter">
        {capturedCount}/{maxPhotos}
      </div>
    </header>

    <div class="camera-content">
      {#if cameraState.error}
        <div class="error-container">
          <div class="error-icon">📷</div>
          <p class="error-message">{cameraState.error}</p>
          <button class="btn btn--secondary" on:click={initializeCamera}> Try Again </button>
        </div>
      {:else if showPreview && lastCapturedPhoto}
        <div class="preview-container">
          <img src={lastCapturedPhoto} alt="" class="preview-image" />
          <div class="preview-actions">
            <button class="btn btn--secondary" on:click={retakePhoto}> Retake </button>
            <button class="btn btn--primary" on:click={acceptPhoto}> Use Photo </button>
          </div>
        </div>
      {:else if cameraState.isActive}
        <div class="video-container">
          <video bind:this={videoElement} class="video-preview" autoplay playsinline muted></video>

          <div class="camera-overlay">
            <div class="viewfinder"></div>
          </div>

          <div class="camera-controls">
            <button class="switch-camera-btn" on:click={switchCamera} aria-label="Switch camera">
              🔄
            </button>

            <button
              class="capture-btn"
              class:capture-btn--capturing={isCapturing}
              on:click={capturePhoto}
              disabled={!canCaptureMore || isCapturing}
              aria-label="Capture photo"
            >
              <div class="capture-btn-inner"></div>
            </button>

            <div class="remaining-counter">
              {remainingPhotos} left
            </div>
          </div>
        </div>
      {:else}
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p>Initializing camera...</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .camera-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--color-overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--space-4);
  }

  .camera-container {
    background: var(--color-background);
    border-radius: var(--radius-xl);
    overflow: hidden;
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }

  .camera-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4);
    border-bottom: 1px solid var(--color-border);
    background: var(--color-background-secondary);
  }

  .close-btn {
    background: none;
    border: none;
    font-size: var(--text-lg);
    cursor: pointer;
    padding: var(--space-2);
    border-radius: var(--radius-md);
    color: var(--color-text-muted);
    transition: all 0.2s ease;
    min-height: 44px;
    min-width: 44px;
  }

  .close-btn:hover {
    background: var(--color-background-tertiary);
    color: var(--color-text-primary);
  }

  .camera-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .photo-counter {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-weight: 500;
  }

  .camera-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .video-container {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .video-preview {
    width: 100%;
    height: 300px;
    object-fit: cover;
    background: var(--color-background-secondary);
  }

  .camera-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
  }

  .viewfinder {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 200px;
    border: 2px solid var(--color-primary);
    border-radius: var(--radius-lg);
    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
  }

  .camera-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6);
    background: var(--color-background);
  }

  .switch-camera-btn {
    background: var(--color-background-secondary);
    border: none;
    font-size: var(--text-xl);
    cursor: pointer;
    padding: var(--space-3);
    border-radius: 50%;
    color: var(--color-text-primary);
    transition: all 0.2s ease;
    min-height: 44px;
    min-width: 44px;
  }

  .switch-camera-btn:hover {
    background: var(--color-background-tertiary);
  }

  .capture-btn {
    background: var(--color-primary);
    border: 4px solid var(--color-background);
    border-radius: 50%;
    cursor: pointer;
    padding: var(--space-2);
    transition: all 0.2s ease;
    min-height: 72px;
    min-width: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .capture-btn:hover:not(:disabled) {
    transform: scale(1.05);
  }

  .capture-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .capture-btn--capturing {
    transform: scale(0.95);
  }

  .capture-btn-inner {
    width: 40px;
    height: 40px;
    background: var(--color-background);
    border-radius: 50%;
  }

  .remaining-counter {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-weight: 500;
    min-width: 44px;
    text-align: center;
  }

  .preview-container {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .preview-image {
    width: 100%;
    height: 300px;
    object-fit: cover;
  }

  .preview-actions {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-6);
  }

  .preview-actions .btn {
    flex: 1;
    min-height: 44px;
  }

  .error-container,
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-8);
    text-align: center;
    min-height: 300px;
  }

  .error-icon {
    font-size: 48px;
    margin-bottom: var(--space-4);
    opacity: 0.5;
  }

  .error-message {
    color: var(--color-text-muted);
    margin-bottom: var(--space-6);
    line-height: 1.5;
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-border);
    border-top: 3px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-4);
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Mobile adjustments */
  @media (max-width: 768px) {
    .camera-modal {
      padding: 0;
    }

    .camera-container {
      max-width: none;
      max-height: none;
      height: 100%;
      border-radius: 0;
    }

    .video-preview {
      height: 50vh;
    }

    .viewfinder {
      width: 150px;
      height: 150px;
    }
  }
</style>
