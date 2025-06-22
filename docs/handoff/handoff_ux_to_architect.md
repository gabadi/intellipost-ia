# UX to Frontend Architect Handoff Document
## IntelliPost AI - MVP Frontend Architecture Requirements

### Document Information
- **From:** UX Design Team
- **To:** Frontend Architect
- **Date:** June 22, 2025
- **Phase:** Frontend Specification Complete → Frontend Architecture Design
- **MVP Scope:** Mobile-Complete, Desktop Post-MVP

---

## Executive Summary

IntelliPost AI MVP implements a **mobile-complete** architecture supporting AI-powered MercadoLibre listing generation. Users capture photos, add prompts, and publish listings through two primary mobile flows based on AI confidence scoring.

**Core Value Proposition:** Photo + Prompt = Ready-to-publish listing in <60 seconds

---

## MVP Scope and Constraints

### MVP Definition: Mobile-Complete
- ✅ **Core:** Mobile Quick Approval flow (high confidence >85%)
- ✅ **Core:** Mobile Balanced Review flow (medium confidence 70-85%)
- ✅ **Handled:** Low confidence (<70%) uses Balanced Review with additional guidance
- 🔄 **Post-MVP:** Desktop power management interface

### Critical Success Metrics
- **Time to First Listing:** <60 seconds from photo capture to published
- **Mobile Completion Rate:** >80% of workflows completed without desktop
- **Processing Performance:** 10-15 seconds typical AI processing
- **Upload Performance:** <5 seconds for multiple photos on mobile network

---

## Core User Flows (MVP)

### 1. Quick Approval Flow (High Confidence >85%)
```
Add Product → Camera Opens → Multiple Photos → Required Prompt → 
AI Processing (10-15s) → Generated Listing → BIG "PUBLISH NOW" → 
Published to MercadoLibre
```

**Secondary Path:** Small "Review Details" link for optional tweaks

### 2. Balanced Review Flow (Medium/Low Confidence ≤85%)
```
Review Generated Listing → "Looks Good" OR "Need Changes" → 
[If Changes] Edit Interface (Prompt + Manual Fields) → 
[If Prompt Changed] AI Regeneration → Publish
```

**Edit Interface supports:**
- **Prompt editing:** Triggers full AI regeneration  
- **Manual tweaks:** Direct field editing (no regeneration)

---

## Critical Frontend Components (MVP)

### 1. Photo Collection Component
**Purpose:** Multi-photo capture and selection
- Direct camera integration (opens immediately on "Add Product")
- Gallery picker for existing photos
- No photo limit (unlimited)
- Preview grid with remove/reorder
- Photo count indicator

### 2. Prompt Input Component  
**Purpose:** Required user description for AI accuracy
- Required field with placeholder: "Describe your item (brand, size, condition...)"
- "Important for accuracy" messaging
- Auto-resize text area
- Regeneration trigger in edit mode

### 3. Processing Spinner Component
**Purpose:** AI processing feedback (10-15 seconds)
- Full screen overlay with spinner
- "Analyzing your photos..." messaging  
- Time estimate display
- No cancel option (keep simple for MVP)

### 4. Generated Listing Preview Component
**Purpose:** Display complete AI-generated listing
- Main product image prominent
- Generated title with AI labeling (🤖)
- Confidence indicator (green/yellow/red)
- Large "PUBLISH NOW" primary button
- Small "Edit Details" secondary link

### 5. Edit Interface Component
**Purpose:** Two-mode editing capability
- **Prompt Section:** Edit original prompt + "Update & Regenerate" button
- **Manual Fields:** Direct editing of title, description, price, category
- Clear visual separation between AI regeneration vs manual tweaks
- Auto-save for manual changes

### Supporting Components
- **Confidence Indicator:** Visual confidence scoring (>85% green, 70-85% yellow, <70% red)
- **Action Button:** Primary/secondary actions with confidence-appropriate styling
- **AI Transparency Labels:** Clear distinction between user content (📝) and AI content (🤖)

---

## Technical Requirements (MVP)

### Performance Targets
- **App Load:** <3 seconds for dashboard on 3G
- **Photo Upload:** <5 seconds for multiple photos
- **AI Processing:** 10-15 seconds typical, 30 seconds maximum
- **UI Response:** <100ms for all interactions
- **Animation:** 60fps for confidence indicators

### Mobile-First Architecture
**Responsive Strategy:**
- **Mobile:** 320px-767px (Core MVP)
- **Tablet:** 768px-1023px (Mobile extended with larger touch targets)
- **Desktop:** 1024px+ (Post-MVP)

**Touch Optimization:**
- Minimum 44px touch targets
- Swipe gestures for image comparison
- No hover states (mobile-first design)
- Single-column layout optimized for one-hand use

### Network Resilience
- **3G Compatibility:** App functional on slower mobile networks
- **Image Compression:** Automatic compression before upload
- **Progressive Upload:** Show UI while photos upload in background
- **Offline Handling:** Cache user inputs during network issues
- **Retry Logic:** Automatic retry on processing failures

---

## State Management Requirements

### Product State Entity
```typescript
interface ProductState {
  id: string;
  userId: string;
  status: 'uploading' | 'processing' | 'ready' | 'published' | 'failed';
  confidence: {
    overall: number; // 0-100
  };
  inputs: {
    prompt: string; // Required field
    images: ImageData[]; // Unlimited count
  };
  outputs: {
    title: string;
    description: string;
    category: string;
    price: number;
    processedImages: ImageData[];
    mainImage: string;
  };
  metadata: {
    createdAt: timestamp;
    updatedAt: timestamp;
  };
}
```

### State Transitions
```
Created → Uploading → Processing → Ready → Published
                           ↓
                        Failed → [Retry/Manual Edit]
```

---

## API Requirements (Frontend Perspective)

### Critical Endpoints
```typescript
// Core product flow
POST /api/products                    // Create with photos + prompt
GET /api/products/{id}/status         // Check processing status
PUT /api/products/{id}/prompt         // Update prompt (triggers regeneration)
PUT /api/products/{id}/fields         // Manual field updates
POST /api/products/{id}/publish       // Publish to MercadoLibre

// Real-time updates
WebSocket /api/products/{id}/updates  // Processing status updates
```

### API Response Requirements
- **Processing status:** Real-time updates during AI processing
- **Confidence scoring:** Overall confidence percentage
- **Error handling:** Clear error messages with retry guidance
- **MercadoLibre integration:** Direct publishing capability

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Components:** Photo Collection + Prompt Input + Processing Spinner + Basic Dashboard
**Goal:** User can capture photos → add prompt → see processing feedback

### Phase 2: AI Integration (Week 3-4)  
**Components:** Generated Listing Preview + Confidence Indicator + Action Button + MercadoLibre publish
**Goal:** Complete Quick Approval flow working end-to-end

### Phase 3: Edit Capabilities (Week 5-6)
**Components:** Edit Interface + AI regeneration + Form validation + Success states  
**Goal:** Full mobile-complete experience (both flows)

### Phase 4: Polish & Optimization (Week 7-8)
**Focus:** Performance optimization + Error handling + UI polish + Testing
**Goal:** Production-ready MVP

---

## Risk Mitigation

### High-Risk Components (Address Early)
1. **Camera Integration:** Test on multiple devices immediately
2. **AI Processing Time:** Mock with realistic delays, plan for timeouts
3. **Photo Upload Performance:** Test on slow networks from start
4. **MercadoLibre API:** Validate publishing integration early

### Fallback Strategies
- **AI Processing Fails:** Edit interface as manual backup
- **Slow Network:** Progressive upload with offline storage
- **Processing Timeout:** Clear error messaging with retry options

---

## Design System Integration

### Color System (MVP-Critical)
- **Primary Blue (#2563EB):** User-generated content labels
- **Accent Purple (#7C3AED):** AI-generated content labels  
- **Success Green (#059669):** High confidence states (>85%)
- **Warning Yellow (#D97706):** Medium confidence states (70-85%)
- **Error Red (#DC2626):** Low confidence states (<70%)

### Typography
- **Primary Font:** Inter (clean, mobile-readable)
- **Type Scale:** H1: 32px, Body: 16px minimum for mobile
- **Line Height:** 1.5 for body text readability

### Spacing
- **Grid System:** 4px base unit
- **Touch Targets:** Minimum 44px for mobile interactions
- **Spacing Scale:** 8px, 16px, 24px, 32px for consistent layouts

---

## Error Handling Strategy

### Critical Error States
```
Upload Failed → Clear retry message → [Try Again] [Cancel]
AI Processing Failed → "Try again or edit manually" → [Retry] [Edit Manually]
Network Issues → Cache inputs → Resume when connected
Processing Timeout → Clear error → Manual editing fallback
```

### User Experience During Errors
- **Clear messaging:** No technical jargon, actionable guidance
- **Retry mechanisms:** Always provide recovery options
- **Fallback paths:** Manual editing when AI fails
- **Progress preservation:** Never lose user inputs

---

## Success Validation

### Implementation Checkpoints
- **Phase 1:** Camera integration working on 3+ device types
- **Phase 2:** Full Quick Approval flow <60 seconds end-to-end
- **Phase 3:** Edit interface supports both prompt and manual editing
- **Phase 4:** App performs on 3G networks with <3 second load

### Ready for Launch Criteria
- ✅ Mobile Quick Approval flow complete
- ✅ Mobile Balanced Review flow complete  
- ✅ Error handling and recovery working
- ✅ Performance targets met on real devices
- ✅ MercadoLibre publishing integration verified

---

## Handoff Artifacts

### Complete Documentation Available
- **Frontend Specification:** `/docs/front-end-spec/` (14 sharded files)
- **Wireframes:** ASCII mockups for all core screens
- **Component Specs:** Detailed component definitions with states
- **User Flows:** Complete flow diagrams for both MVP paths

### Design System Resources
- **Color palette:** Complete with hex codes and usage
- **Typography scale:** Defined for mobile-first implementation
- **Component library:** All MVP components specified with variants
- **Responsive strategy:** Mobile-complete breakpoint specifications

---

*This handoff provides everything needed to architect and implement the IntelliPost AI MVP frontend. Focus on mobile-complete functionality with simple, fast user flows that emphasize AI automation over manual configuration.*