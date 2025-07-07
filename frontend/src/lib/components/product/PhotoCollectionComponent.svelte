<script lang="ts">
  import type { ProductImageData } from '../../types/product';
  import { validateImageFile } from '../../utils/validation';
  import { processImageFile } from '../../utils/image';
  import { isCameraSupported } from '../../utils/camera';
  import { productCreationStore } from '../../stores/product-creation';
  import CameraCapture from './CameraCapture.svelte';
  import ImageThumbnail from './ImageThumbnail.svelte';

  export let images: ProductImageData[] = [];
  export let maxImages = 8;
  export let disabled = false;

  let fileInput: HTMLInputElement;
  let dragover = false;
  let uploading = false;
  let showCamera = false;
  let uploadProgress: Record<string, number> = {};
  let errors: string[] = [];

  // Reactive statements for image management
  $: imageCount = Array.isArray(images) ? images.length : 0;
  $: canAddMore = imageCount < maxImages;
  $: remainingSlots = maxImages - imageCount;

  function handleFileInput(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files) {
      handleFiles(Array.from(target.files));
    }
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragover = false;

    if (event.dataTransfer?.files) {
      handleFiles(Array.from(event.dataTransfer.files));
    }
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    dragover = true;
  }

  function handleDragLeave() {
    dragover = false;
  }

  async function handleFiles(files: File[]) {
    if (!canAddMore) {
      addError(`Maximum ${maxImages} images allowed`);
      return;
    }

    const filesToProcess = files.slice(0, remainingSlots);
    uploading = true;
    errors = [];

    try {
      const processedImages: ProductImageData[] = [];

      for (const file of filesToProcess) {
        try {
          // Validate file
          const fileValidation = await validateImageFile(file);
          if (!fileValidation.isValid) {
            addError(`${file.name}: ${fileValidation.message}`);
            continue;
          }

          // Track upload progress
          const imageId = crypto.randomUUID();
          uploadProgress[imageId] = 0;

          // Process image
          const processedImage = await processImageFile(file);
          processedImage.id = imageId;

          // Set as primary if it's the first image
          if (imageCount === 0 && processedImages.length === 0) {
            processedImage.is_primary = true;
          }

          processedImages.push(processedImage);
          uploadProgress[imageId] = 100;
        } catch {
          addError(`${file.name}: Failed to process image`);
        }
      }

      if (processedImages.length > 0) {
        // Update the store directly instead of local state
        productCreationStore.addImages(processedImages);
      }
    } finally {
      uploading = false;
      uploadProgress = {};
    }
  }

  function handleCameraPhoto(file: File) {
    handleFiles([file]);
    showCamera = false;
  }

  function removeImage(event: CustomEvent<{ imageId: string }>) {
    const { imageId } = event.detail;
    productCreationStore.removeImage(imageId);
  }

  function setPrimaryImage(event: CustomEvent<{ imageId: string }>) {
    const { imageId } = event.detail;
    productCreationStore.setPrimaryImage(imageId);
  }

  function reorderImages(event: CustomEvent<{ startIndex: number; endIndex: number }>) {
    const { startIndex, endIndex } = event.detail;
    productCreationStore.reorderImages(startIndex, endIndex);
  }

  function openFileDialog() {
    fileInput?.click();
  }

  function openCamera() {
    showCamera = true;
  }

  function closeCamera() {
    showCamera = false;
  }

  function addError(message: string) {
    errors = [...errors, message];
    setTimeout(() => {
      errors = errors.filter(err => err !== message);
    }, 5000);
  }

  // Utility function for manual error clearing if needed
  // function clearErrors() {
  //   errors = [];
  // }
</script>

<div class="photo-collection">
  <div class="collection-header">
    <h3 class="collection-title">Product Photos</h3>
    <span class="image-counter">
      {imageCount}/{maxImages}
    </span>
  </div>

  {#if errors.length > 0}
    <div class="error-messages">
      {#each errors as error}
        <div class="error-message">
          <span class="error-icon">⚠</span>
          {error}
          <button class="error-close" on:click={() => (errors = errors.filter(e => e !== error))}>
            ✕
          </button>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Upload Zone -->
  {#if canAddMore}
    <div
      class="upload-zone"
      class:upload-zone--dragover={dragover}
      class:upload-zone--uploading={uploading}
      on:drop={handleDrop}
      on:dragover={handleDragOver}
      on:dragleave={handleDragLeave}
      role="button"
      tabindex="0"
      aria-label="Upload images"
    >
      <input
        bind:this={fileInput}
        type="file"
        multiple
        accept=".jpg,.jpeg,.png"
        on:change={handleFileInput}
        {disabled}
        style="display: none;"
      />

      {#if uploading}
        <div class="upload-progress">
          <div class="loading-spinner"></div>
          <p>Processing images...</p>
        </div>
      {:else}
        <div class="upload-content">
          <div class="upload-icon">📷</div>
          <h4 class="upload-title">Add Product Photos</h4>
          <p class="upload-subtitle">Drag & drop images or click to browse</p>

          <div class="upload-actions">
            {#if isCameraSupported()}
              <button class="btn btn--primary upload-btn" on:click={openCamera} {disabled}>
                📷 Take Photos
              </button>
            {/if}

            <button class="btn btn--secondary upload-btn" on:click={openFileDialog} {disabled}>
              📁 Browse Files
            </button>
          </div>

          <div class="upload-info">
            <p class="upload-limit">
              Up to {remainingSlots} more image{remainingSlots === 1 ? '' : 's'}
            </p>
            <p class="upload-requirements">JPG, PNG • Max 10MB each • Min 800×600px</p>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Image Grid -->
  {#if images.length > 0}
    <div class="image-grid">
      {#each images as image, index (image.id)}
        <ImageThumbnail
          {image}
          {index}
          isPrimary={image.is_primary}
          on:remove={removeImage}
          on:setPrimary={setPrimaryImage}
          on:reorder={reorderImages}
        />
      {/each}
    </div>

    <div class="collection-info">
      <p class="primary-info">⭐ Primary image will be shown first in your listing</p>
      {#if images.length > 1}
        <p class="reorder-info">💡 Drag images to reorder them</p>
      {/if}
    </div>
  {/if}

  <!-- Validation Message - remove local validation display, let parent handle it -->
</div>

{#if showCamera}
  <CameraCapture
    onPhotoCapture={handleCameraPhoto}
    onClose={closeCamera}
    maxPhotos={maxImages}
    capturedCount={images.length}
  />
{/if}

<style>
  .photo-collection {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    width: 100%;
  }

  .collection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .collection-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .image-counter {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-weight: 500;
    background: var(--color-background-secondary);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-full);
  }

  .error-messages {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3);
    background: var(--color-error-light);
    border: 1px solid var(--color-error);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    color: var(--color-error-dark);
  }

  .error-icon {
    font-size: var(--text-base);
  }

  .error-close {
    background: none;
    border: none;
    cursor: pointer;
    font-size: var(--text-sm);
    color: var(--color-error);
    margin-left: auto;
    padding: var(--space-1);
    border-radius: var(--radius-sm);
    transition: background-color 0.2s ease;
  }

  .error-close:hover {
    background: var(--color-error);
    color: var(--color-background);
  }

  .upload-zone {
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    text-align: center;
    transition: all 0.2s ease;
    background: var(--color-background-secondary);
    cursor: pointer;
  }

  .upload-zone:hover {
    border-color: var(--color-primary);
    background: var(--color-primary-light);
  }

  .upload-zone--dragover {
    border-color: var(--color-primary);
    background: var(--color-primary-light);
    transform: scale(1.02);
  }

  .upload-zone--uploading {
    border-color: var(--color-border);
    background: var(--color-background-secondary);
    cursor: default;
  }

  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
  }

  .upload-icon {
    font-size: 48px;
    opacity: 0.7;
  }

  .upload-title {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .upload-subtitle {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    margin: 0;
  }

  .upload-actions {
    display: flex;
    gap: var(--space-3);
    flex-wrap: wrap;
    justify-content: center;
  }

  .upload-btn {
    min-height: 44px;
    min-width: 120px;
  }

  .upload-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    text-align: center;
  }

  .upload-limit {
    font-size: var(--text-sm);
    color: var(--color-text-primary);
    font-weight: 500;
    margin: 0;
  }

  .upload-requirements {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    margin: 0;
  }

  .upload-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-border);
    border-top: 3px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: var(--space-3);
    width: 100%;
  }

  .collection-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-3);
    background: var(--color-background-secondary);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--color-primary);
  }

  .primary-info,
  .reorder-info {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    margin: 0;
    line-height: 1.4;
  }

  /* Removed unused validation message styles - validation now handled by parent */

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Mobile optimizations */
  @media (max-width: 768px) {
    .upload-zone {
      padding: var(--space-4);
    }

    .upload-actions {
      flex-direction: column;
      width: 100%;
    }

    .upload-btn {
      width: 100%;
    }

    .image-grid {
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: var(--space-2);
    }

    .collection-info {
      padding: var(--space-2);
    }

    .upload-icon {
      font-size: 36px;
    }

    .upload-title {
      font-size: var(--text-base);
    }
  }
</style>
