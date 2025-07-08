import type { ImageCompression, ProductImageData } from '../types/product';
import { DEFAULT_IMAGE_COMPRESSION } from '../types/product';

export function compressImage(file: File, options: Partial<ImageCompression> = {}): Promise<File> {
  return new Promise((resolve, reject) => {
    const config = { ...DEFAULT_IMAGE_COMPRESSION, ...options };

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      // Calculate new dimensions maintaining aspect ratio
      let { width, height } = img;

      if (width > config.maxWidth || height > config.maxHeight) {
        const aspectRatio = width / height;

        if (width > height) {
          width = config.maxWidth;
          height = width / aspectRatio;
        } else {
          height = config.maxHeight;
          width = height * aspectRatio;
        }
      }

      canvas.width = width;
      canvas.height = height;

      // Draw and compress
      ctx?.drawImage(img, 0, 0, width, height);

      canvas.toBlob(
        blob => {
          if (!blob) {
            reject(new Error('Failed to compress image'));
            return;
          }

          const compressedFile = new File([blob], file.name, {
            type: `image/${config.outputFormat}`,
            lastModified: Date.now(),
          });

          resolve(compressedFile);
        },
        `image/${config.outputFormat}`,
        config.quality
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      reject(new Error('Failed to load image for compression'));
    };

    img.src = URL.createObjectURL(file);
  });
}

export function correctImageOrientation(file: File): Promise<File> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      // Get EXIF orientation data
      getOrientation(file, orientation => {
        const { width, height } = img;

        canvas.width = width;
        canvas.height = height;

        // Apply orientation correction
        if (ctx) {
          switch (orientation) {
            case 2:
              ctx.transform(-1, 0, 0, 1, width, 0);
              break;
            case 3:
              ctx.transform(-1, 0, 0, -1, width, height);
              break;
            case 4:
              ctx.transform(1, 0, 0, -1, 0, height);
              break;
            case 5:
              canvas.width = height;
              canvas.height = width;
              ctx.transform(0, 1, 1, 0, 0, 0);
              break;
            case 6:
              canvas.width = height;
              canvas.height = width;
              ctx.transform(0, 1, -1, 0, height, 0);
              break;
            case 7:
              canvas.width = height;
              canvas.height = width;
              ctx.transform(0, -1, -1, 0, height, width);
              break;
            case 8:
              canvas.width = height;
              canvas.height = width;
              ctx.transform(0, -1, 1, 0, 0, width);
              break;
          }
        }

        ctx?.drawImage(img, 0, 0);

        canvas.toBlob(
          blob => {
            if (!blob) {
              reject(new Error('Failed to correct orientation'));
              return;
            }

            const correctedFile = new File([blob], file.name, {
              type: file.type,
              lastModified: Date.now(),
            });

            resolve(correctedFile);
          },
          file.type,
          0.9
        );
      });
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      reject(new Error('Failed to load image for orientation correction'));
    };

    img.src = URL.createObjectURL(file);
  });
}

function getOrientation(file: File, callback: (orientation: number) => void): void {
  const reader = new FileReader();

  reader.onload = event => {
    const view = new DataView(event.target?.result as ArrayBuffer);

    if (view.getUint16(0, false) !== 0xffd8) {
      callback(1); // Not a JPEG
      return;
    }

    const length = view.byteLength;
    let offset = 2;

    while (offset < length) {
      const marker = view.getUint16(offset, false);
      offset += 2;

      if (marker === 0xffe1) {
        offset += 2;

        if (view.getUint32(offset, false) !== 0x45786966) {
          callback(1);
          return;
        }

        const tiffOffset = offset + 6;
        const firstIFDOffset = view.getUint32(tiffOffset + 4, false);
        const entriesCount = view.getUint16(tiffOffset + firstIFDOffset, false);

        for (let i = 0; i < entriesCount; i++) {
          const entryOffset = tiffOffset + firstIFDOffset + 2 + i * 12;
          const tag = view.getUint16(entryOffset, false);

          if (tag === 0x0112) {
            const orientation = view.getUint16(entryOffset + 8, false);
            callback(orientation);
            return;
          }
        }
      }

      offset += view.getUint16(offset, false);
    }

    callback(1);
  };

  reader.readAsArrayBuffer(file);
}

export function createImageThumbnail(file: File, size = 150): Promise<string> {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      const { width, height } = img;
      const aspectRatio = width / height;

      canvas.width = size;
      canvas.height = size;

      let drawWidth = size;
      let drawHeight = size;
      let offsetX = 0;
      let offsetY = 0;

      if (aspectRatio > 1) {
        drawHeight = size / aspectRatio;
        offsetY = (size - drawHeight) / 2;
      } else {
        drawWidth = size * aspectRatio;
        offsetX = (size - drawWidth) / 2;
      }

      ctx?.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);

      resolve(canvas.toDataURL('image/jpeg', 0.8));
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      reject(new Error('Failed to create thumbnail'));
    };

    img.src = URL.createObjectURL(file);
  });
}

export async function processImageFile(file: File): Promise<ProductImageData> {
  const startTime = Date.now();

  // Get original metadata
  const originalMetadata = await getImageMetadata(file);

  // Compress image
  const compressedFile = await compressImage(file);

  // Correct orientation if needed
  const correctedFile = await correctImageOrientation(compressedFile);

  const processingTime = Date.now() - startTime;

  const productImage: ProductImageData = {
    id: crypto.randomUUID(),
    file: correctedFile,
    file_size_bytes: correctedFile.size,
    file_format: correctedFile.type.split('/')[1] as 'jpg' | 'jpeg' | 'png' | 'webp',
    resolution_width: originalMetadata.width,
    resolution_height: originalMetadata.height,
    is_primary: false,
    processing_metadata: {
      compressed_size_bytes: correctedFile.size,
      processing_time_ms: processingTime,
    },
  };

  return productImage;
}

async function getImageMetadata(file: File): Promise<{
  width: number;
  height: number;
  size: number;
  format: string;
}> {
  return new Promise((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      resolve({
        width: img.width,
        height: img.height,
        size: file.size,
        format: file.type.split('/')[1] || 'unknown',
      });
    };

    img.onerror = () => {
      URL.revokeObjectURL(img.src); // Clean up memory leak
      reject(new Error('Failed to load image'));
    };

    img.src = URL.createObjectURL(file);
  });
}
