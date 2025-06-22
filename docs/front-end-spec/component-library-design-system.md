# Component Library / Design System

**Design System Approach:** Custom design system optimized for mobile-first, confidence-driven interfaces

## Core Components

### Photo Collection Component

**Purpose:** Enable users to capture and select multiple photos for product listings

**Variants:** Camera mode, Gallery mode, Preview grid

**States:** Empty, Adding photos, Preview mode, Error state

**Key Features:**
- Direct camera integration with immediate trigger
- Gallery picker for existing photos
- Photo count indicator (e.g., "3 photos")
- Preview grid with remove/reorder capabilities
- No limit on photo count
- Clear "Done" or "Continue" action

**Usage Guidelines:**
- Camera opens immediately on "Add Product" tap
- Switch between camera/gallery with clear toggle
- Photos show in grid with easy removal option
- Continue button becomes prominent once photos added

### Prompt Input Component

**Purpose:** Capture user descriptions to enhance AI accuracy

**Variants:** Initial prompt, Edit prompt (with regeneration)

**States:** Empty, Active, Filled, Processing, Error

**Key Features:**
- Prominent placeholder: "Describe your item (brand, size, condition...)"
- Character limit indicator (if needed)
- Auto-resize text area
- "Important for accuracy" messaging
- Regeneration trigger when in edit mode

**Usage Guidelines:**
- Required field with clear importance messaging
- Focus automatically when screen loads
- Show examples or hints for better prompts
- In edit mode, show "Update & Regenerate" button when changed

### Confidence Indicator

**Purpose:** Visual representation of AI confidence levels with appropriate messaging

**Variants:** High (>85%), Medium (70-85%), Low (<70%)

**States:** Static display, animated processing, interactive tooltip

**Usage Guidelines:**
- High confidence: Green color, encouraging messaging ("Ready to publish!")
- Medium confidence: Yellow color, verification messaging ("Good, please verify")
- Low confidence: Red color, attention messaging ("Needs attention")

### Processing Spinner Component

**Purpose:** Provide feedback during AI processing with clear messaging

**Variants:** Initial processing, Regeneration processing

**States:** Loading, Progress indication, Error, Timeout

**Key Features:**
- Simple spinner animation
- Clear messaging: "Analyzing your photos..."
- Time estimate: "This usually takes 10-15 seconds"
- Consistent branding with accent purple color
- No cancel option (keep it simple for MVP)

**Usage Guidelines:**
- Full screen overlay to prevent other actions
- Encouraging messaging to build confidence
- Consistent animation speed and styling
- Clear transition to results screen

### Image Comparison Slider

**Purpose:** Before/after comparison for AI-processed images

**Variants:** Mobile swipe, Desktop slider, Thumbnail grid

**States:** Loading, Interactive, Comparison mode

**Usage Guidelines:**
- Mobile: Swipe gesture with clear indicators
- Desktop: Drag slider with precise control
- Always show processing indicators during AI enhancement

### Generated Listing Preview Component

**Purpose:** Display complete AI-generated listing for user review and approval

**Variants:** High confidence view, Medium confidence view, Edit mode

**States:** Loading, Complete, Editing, Publishing

**Key Features:**
- Main product image prominent at top
- Generated title with clear AI labeling (🤖)
- Price, category, and description sections
- Confidence indicator for overall listing
- Large "PUBLISH NOW" primary action button
- Small "Edit Details" secondary link
- Clear visual hierarchy emphasizing automation

**Usage Guidelines:**
- Title should be large and attention-grabbing
- Use AI transparency labeling consistently
- Primary action button uses success green color
- Secondary action is subtle, not competing
- Show confidence level prominently but positively

### Action Button

**Purpose:** Primary and secondary actions with confidence-appropriate styling

**Variants:** Primary (Publish), Secondary (Edit), Tertiary (Cancel), Destructive (Delete)

**States:** Default, Hover, Active, Disabled, Loading

**Usage Guidelines:**
- Primary actions match confidence level (green for high confidence)
- Loading states show processing indicators
- Disabled states provide clear feedback on requirements

#### AI Transparency Components

**Purpose:** Clear visual differentiation between user and AI-generated content

**Content Labeling Strategy:**
- **📝 Your Original:** User-provided content with primary blue styling (#2563EB)
- **🤖 AI Generated:** System-created content with accent purple styling (#7C3AED) and confidence indicators
- **📷→🤖 Enhanced:** Processed images showing transformation with accent styling

**Visual Hierarchy:**
- High confidence: Bold, encouraging messaging
- Medium confidence: Neutral, verification-focused messaging
- Low confidence: Attention-grabbing but not alarming messaging

### Product Status Card

**Purpose:** Compact product representation with status and actions

**Variants:** Dashboard card, List item, Detailed view

**States:** Processing, Ready, Needs attention, Published, Error

**Usage Guidelines:**
- Color coding matches confidence system
- Clear next action indicated
- Status changes animate smoothly

### Edit Interface Component

**Purpose:** Comprehensive editing interface for listing adjustments

**Variants:** Prompt editing (with regeneration), Manual field editing

**States:** Default, Editing prompt, Editing fields, Regenerating, Saving

**Key Features:**
- **Prompt Section:** Original prompt with edit capability + "Update & Regenerate" button
- **Manual Fields:** Title, description, price, category for direct editing
- **Clear separation** between AI regeneration and manual tweaks
- Auto-save for manual changes
- Regeneration progress feedback

**Usage Guidelines:**
- Prompt editing triggers full AI regeneration
- Manual field changes are immediate (no regeneration)
- Clear labeling of which fields will regenerate vs. manual save
- "Update & Regenerate" button only appears when prompt is changed
- Maintain AI transparency labels throughout
