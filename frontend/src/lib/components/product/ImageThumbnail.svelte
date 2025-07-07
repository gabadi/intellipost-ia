<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import type { ProductImageData } from '../../types/product';
  import { createImageThumbnail } from '../../utils/image';
  import { formatFileSize } from '../../utils/validation';

  export let image: ProductImageData;
  export let index: number;
  export let isPrimary: boolean;
  export let isDragging = false;
  export let showMetadata = false;

  const dispatch = createEventDispatcher<{
    remove: { imageId: string };
    setPrimary: { imageId: string };
    reorder: { startIndex: number; endIndex: number };
    preview: { imageId: string };
  }>();

  let thumbnailUrl: string | null = null;
  let dragStartIndex: number | null = null;
  let showConfirmDelete = false;

  onMount(() => {
    async function setupThumbnail() {
      try {
        thumbnailUrl = await createImageThumbnail(image.file);
      } catch {
        // Fallback to object URL if thumbnail creation fails
        // Fallback to object URL
        thumbnailUrl = URL.createObjectURL(image.file);
      }
    }

    setupThumbnail();

    return () => {
      if (thumbnailUrl) {
        URL.revokeObjectURL(thumbnailUrl);
      }
    };
  });

  function handleRemove() {
    showConfirmDelete = true;
  }

  function confirmRemove() {
    dispatch('remove', { imageId: image.id });
    showConfirmDelete = false;
  }

  function cancelRemove() {
    showConfirmDelete = false;
  }

  function handleSetPrimary() {
    if (!isPrimary) {
      dispatch('setPrimary', { imageId: image.id });
    }
  }

  function handlePreview() {
    dispatch('preview', { imageId: image.id });
  }

  // Drag and drop handlers
  function handleDragStart(event: DragEvent) {
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', index.toString());
      dragStartIndex = index;
    }
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move';
    }
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();

    if (dragStartIndex !== null && dragStartIndex !== index) {
      dispatch('reorder', {
        startIndex: dragStartIndex,
        endIndex: index,
      });
    }

    dragStartIndex = null;
  }

  function handleDragEnd() {
    dragStartIndex = null;
  }

  // Touch handlers for mobile drag-and-drop
  let touchStartY = 0;
  let touchStartX = 0;

  function handleTouchStart(event: TouchEvent) {
    const touch = event.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
  }

  function handleTouchMove(event: TouchEvent) {
    event.preventDefault();
    // Visual feedback for drag could be added here
  }

  function handleTouchEnd(event: TouchEvent) {
    const touch = event.changedTouches[0];
    const deltaX = Math.abs(touch.clientX - touchStartX);
    const deltaY = Math.abs(touch.clientY - touchStartY);

    // If it's a small movement, treat as tap
    if (deltaX < 10 && deltaY < 10) {
      handlePreview();
    }
  }
</script>

<div
  class="image-thumbnail"
  class:image-thumbnail--primary={isPrimary}
  class:image-thumbnail--dragging={isDragging}
  draggable="true"
  on:dragstart={handleDragStart}
  on:dragover={handleDragOver}
  on:drop={handleDrop}
  on:dragend={handleDragEnd}
  on:touchstart={handleTouchStart}
  on:touchmove={handleTouchMove}
  on:touchend={handleTouchEnd}
  role="button"
  tabindex="0"
  aria-label="Product image {index + 1}{isPrimary ? ' (primary)' : ''}"
>
  <div class="thumbnail-container">
    {#if thumbnailUrl}
      <button
        class="thumbnail-image-button"
        on:click={handlePreview}
        on:keydown={e => e.key === 'Enter' && handlePreview()}
        aria-label="Preview product image {index + 1}"
      >
        <img src={thumbnailUrl} alt="Product image {index + 1}" class="thumbnail-image" />
      </button>
    {:else}
      <div class="thumbnail-loading">
        <div class="loading-spinner"></div>
      </div>
    {/if}

    {#if isPrimary}
      <div class="primary-badge">⭐ Primary</div>
    {/if}

    <div class="thumbnail-actions">
      <button
        class="action-btn action-btn--primary"
        class:action-btn--active={isPrimary}
        on:click|stopPropagation={handleSetPrimary}
        aria-label={isPrimary ? 'Primary image' : 'Set as primary'}
        title={isPrimary ? 'Primary image' : 'Set as primary'}
      >
        {isPrimary ? '⭐' : '☆'}
      </button>

      <button
        class="action-btn action-btn--danger"
        on:click|stopPropagation={handleRemove}
        aria-label="Remove image"
        title="Remove image"
      >
        🗑
      </button>
    </div>

    <div class="drag-handle" aria-label="Drag to reorder">⋮⋮</div>
  </div>

  {#if showMetadata}
    <div class="image-metadata">
      <div class="metadata-item">
        <span class="metadata-label">Size:</span>
        <span class="metadata-value">{formatFileSize(image.file_size_bytes)}</span>
      </div>
      <div class="metadata-item">
        <span class="metadata-label">Dimensions:</span>
        <span class="metadata-value">{image.resolution_width}×{image.resolution_height}</span>
      </div>
      <div class="metadata-item">
        <span class="metadata-label">Format:</span>
        <span class="metadata-value">{image.file_format.toUpperCase()}</span>
      </div>
    </div>
  {/if}
</div>

{#if showConfirmDelete}
  <div class="confirm-modal">
    <div class="confirm-content">
      <h3>Remove Image?</h3>
      <p>This action cannot be undone.</p>
      <div class="confirm-actions">
        <button class="btn btn--secondary" on:click={cancelRemove}> Cancel </button>
        <button class="btn btn--danger" on:click={confirmRemove}> Remove </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .image-thumbnail {
    position: relative;
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: all 0.2s ease;
    cursor: grab;
    background: var(--color-background-secondary);
  }

  .image-thumbnail:active {
    cursor: grabbing;
  }

  .image-thumbnail--primary {
    border: 3px solid var(--color-primary);
    box-shadow: 0 4px 12px var(--color-primary-light);
  }

  .image-thumbnail--dragging {
    opacity: 0.5;
    transform: rotate(5deg);
  }

  .thumbnail-container {
    position: relative;
    width: 100%;
    height: 120px;
    overflow: hidden;
  }

  .thumbnail-image-button {
    width: 100%;
    height: 100%;
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    transition: transform 0.2s ease;
  }

  .thumbnail-image-button:hover {
    transform: scale(1.05);
  }

  .thumbnail-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .thumbnail-loading {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-background-tertiary);
  }

  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--color-border);
    border-top: 2px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .primary-badge {
    position: absolute;
    top: var(--space-2);
    left: var(--space-2);
    background: var(--color-primary);
    color: var(--color-background);
    font-size: var(--text-xs);
    font-weight: 600;
    padding: var(--space-1) var(--space-2);
    border-radius: var(--radius-full);
    z-index: 2;
  }

  .thumbnail-actions {
    position: absolute;
    top: var(--space-2);
    right: var(--space-2);
    display: flex;
    gap: var(--space-1);
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 2;
  }

  .image-thumbnail:hover .thumbnail-actions,
  .image-thumbnail:focus-within .thumbnail-actions {
    opacity: 1;
  }

  .action-btn {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    cursor: pointer;
    padding: var(--space-1);
    transition: all 0.2s ease;
    min-height: 32px;
    min-width: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .action-btn:hover {
    background: var(--color-background-secondary);
  }

  .action-btn--primary.action-btn--active {
    background: var(--color-primary);
    color: var(--color-background);
    border-color: var(--color-primary);
  }

  .action-btn--danger:hover {
    background: var(--color-error);
    color: var(--color-background);
    border-color: var(--color-error);
  }

  .drag-handle {
    position: absolute;
    bottom: var(--space-2);
    right: var(--space-2);
    color: var(--color-text-muted);
    font-size: var(--text-xs);
    opacity: 0;
    transition: opacity 0.2s ease;
    cursor: grab;
    background: var(--color-background);
    border-radius: var(--radius-sm);
    padding: var(--space-1);
    line-height: 1;
  }

  .image-thumbnail:hover .drag-handle {
    opacity: 1;
  }

  .image-metadata {
    padding: var(--space-2);
    background: var(--color-background-secondary);
    border-top: 1px solid var(--color-border);
  }

  .metadata-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-1);
  }

  .metadata-item:last-child {
    margin-bottom: 0;
  }

  .metadata-label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    font-weight: 500;
  }

  .metadata-value {
    font-size: var(--text-xs);
    color: var(--color-text-primary);
    font-weight: 600;
  }

  .confirm-modal {
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
  }

  .confirm-content {
    background: var(--color-background);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    text-align: center;
    max-width: 300px;
    margin: var(--space-4);
  }

  .confirm-content h3 {
    margin: 0 0 var(--space-2) 0;
    color: var(--color-text-primary);
  }

  .confirm-content p {
    margin: 0 0 var(--space-4) 0;
    color: var(--color-text-muted);
    font-size: var(--text-sm);
  }

  .confirm-actions {
    display: flex;
    gap: var(--space-3);
    justify-content: center;
  }

  .confirm-actions .btn {
    min-height: 44px;
    min-width: 80px;
  }

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
    .thumbnail-container {
      height: 100px;
    }

    .thumbnail-actions {
      opacity: 1; /* Always show on mobile */
    }

    .drag-handle {
      opacity: 1; /* Always show on mobile */
    }

    .action-btn {
      min-height: 36px;
      min-width: 36px;
    }
  }
</style>
