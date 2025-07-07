# Test Fixtures

This directory contains test fixtures for the frontend tests.

## Images

The test images are simple colored rectangles generated for testing purposes:

- `test-image-1.jpg` - Red 1920x1080 image (~50KB)
- `test-image-2.jpg` - Green 1920x1080 image (~50KB)
- `test-image-3.jpg` - Blue 1920x1080 image (~50KB)

These images are used in:

- Unit tests for image processing functions
- Integration tests for the photo upload component
- E2E tests for the complete product creation workflow

## Generating Test Images

You can regenerate these test images using the provided script:

```bash
npm run generate-test-fixtures
```

Or manually create them using any image editor with the following specifications:

- Format: JPEG
- Dimensions: 1920x1080
- Size: ~50KB each
- Colors: Red (#FF0000), Green (#00FF00), Blue (#0000FF)
