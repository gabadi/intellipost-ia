import type { CameraCapture } from '../types/product';

export class CameraService {
  private stream: MediaStream | null = null;
  private videoElement: HTMLVideoElement | null = null;

  async requestCameraPermission(): Promise<CameraCapture> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
      });

      this.stream = stream;

      return {
        stream,
        isActive: true,
        permissionStatus: 'granted',
        error: null,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Camera access denied';

      return {
        stream: null,
        isActive: false,
        permissionStatus: 'denied',
        error: errorMessage,
      };
    }
  }

  async stopCamera(): Promise<void> {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
  }

  async startVideoPreview(videoElement: HTMLVideoElement): Promise<void> {
    if (!this.stream) {
      throw new Error('No camera stream available');
    }

    this.videoElement = videoElement;
    videoElement.srcObject = this.stream;

    return new Promise((resolve, reject) => {
      videoElement.onloadedmetadata = () => {
        videoElement
          .play()
          .then(() => resolve())
          .catch(reject);
      };
    });
  }

  async capturePhoto(): Promise<File> {
    if (!this.videoElement || !this.stream) {
      throw new Error('Camera not initialized');
    }

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Could not get canvas context');
    }

    const { videoWidth, videoHeight } = this.videoElement;
    canvas.width = videoWidth;
    canvas.height = videoHeight;

    ctx.drawImage(this.videoElement, 0, 0);

    return new Promise((resolve, reject) => {
      canvas.toBlob(
        blob => {
          if (!blob) {
            reject(new Error('Failed to capture photo'));
            return;
          }

          const file = new File([blob], `photo_${Date.now()}.jpg`, {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });

          resolve(file);
        },
        'image/jpeg',
        0.9
      );
    });
  }

  async switchCamera(): Promise<void> {
    if (!this.stream) {
      throw new Error('No camera stream available');
    }

    const videoTrack = this.stream.getVideoTracks()[0];
    const currentFacingMode = videoTrack.getSettings().facingMode;

    await this.stopCamera();

    const newFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';

    const newStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: newFacingMode,
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
    });

    this.stream = newStream;

    if (this.videoElement) {
      this.videoElement.srcObject = newStream;
    }
  }

  async checkCameraAvailability(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'videoinput');
    } catch {
      return false;
    }
  }

  async getCameraList(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.filter(device => device.kind === 'videoinput');
    } catch {
      return [];
    }
  }
}

export function isCameraSupported(): boolean {
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

export function getCameraErrorMessage(error: Error): string {
  if (error.name === 'NotAllowedError') {
    return 'Camera access was denied. Please allow camera permissions in your browser settings.';
  }

  if (error.name === 'NotFoundError') {
    return 'No camera was found on your device.';
  }

  if (error.name === 'NotSupportedError') {
    return 'Camera is not supported by your browser.';
  }

  if (error.name === 'NotReadableError') {
    return 'Camera is already in use by another application.';
  }

  if (error.name === 'OverconstrainedError') {
    return 'Camera constraints could not be satisfied.';
  }

  return 'An unknown camera error occurred. Please try again.';
}

export function createCameraService(): CameraService {
  return new CameraService();
}
