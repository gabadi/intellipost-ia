# Wireframes & Mockups

**Primary Design Files:** To be created in Figma following this specification

## Key Screen Layouts

### Mobile Dashboard

**Purpose:** Central hub for managing all products with priority-based organization

```
┌─────────────────────────────┐
│ [IntelliPost AI]        ⚙️  │
├─────────────────────────────┤
│                             │
│   📷 [Add New Product]      │
│                             │
├─────────────────────────────┤
│ READY TO PUBLISH (1)        │
│                             │
│ 🟢 Nike Shoes               │
│    [PUBLISH NOW]            │
│                             │
├─────────────────────────────┤
│ NEEDS ATTENTION (2)         │
│                             │
│ 🟡 iPhone Case              │
│    [REVIEW]                 │
│                             │
│ 🔴 Laptop Stand             │
│    [FIX]                    │
│                             │
├─────────────────────────────┤
│ PUBLISHED (1)               │
│                             │
│ ✅ Gaming Chair             │
│                             │
│    [View all products (4)]  │
└─────────────────────────────┘
```

**Organization Principles:**
- **Priority sections:** Ready to Publish (urgent) → Needs Attention → Published (historical)
- **Clear status indicators:** Color-coded status with appropriate actions
- **Action-oriented:** Each item shows the next logical action
- **Scalable display:** Shows 3-4 key items with "View all" for additional products

**Interaction Notes:** Touch-optimized with large tap targets, swipe gestures for secondary actions

**Design File Reference:** figma-mobile-dashboard.fig

### Mobile Review Screen (Tier 1 - High Confidence)

**Purpose:** Quick approval interface for high-confidence AI results

#### Tier 1: Quick Approval (85%+ confidence)
```
┌─────────────────────────────┐
│ 🟢 Ready to publish! 87%    │
├─────────────────────────────┤
│ [Product Image] 📷→🤖       │ ← Swipe: Original ↔ AI Enhanced
│                             │
│ 🤖 Zapatillas Nike Air Max  │
│ Running Hombre Talla 42     │
│                             │
│ 👟 Shoes > Athletic         │
│                             │
│   [    PUBLISH NOW    ]     │ ← Primary action
│   [    Review Details ]     │ ← Secondary option
└─────────────────────────────┘
```

**Key Features:**
- Prominent confidence indicator with positive messaging
- Single main image with swipe comparison (original ↔ AI enhanced)
- Essential information visible (title, category)
- Large "Publish Now" button for quick approval
- Secondary option for users who want to review details

#### Tier 2: Balanced Review (70-85% confidence)
```
┌─────────────────────────────┐
│ 🟡 Good, please verify 78%  │
├─────────────────────────────┤
│ [Product Image] 📷→🤖       │
│ ▼ Compare all images        │ ← Expandable section
│                             │
│ 🤖 Title: Nike Air Max...   │
│ 📝 Your prompt: "Nike 42"  │
│                             │
│ Category: 👟 Shoes (90%)    │ ← Component confidence
│ Attributes: ✓ Nike ✓ 42    │
│                             │
│ [    LOOKS GOOD    ]        │
│ [    NEED CHANGES  ]        │
└─────────────────────────────┘
```

**Key Features:**
- Neutral confidence messaging encouraging verification
- Shows both AI output and original user input for context
- Component-level confidence scores for transparency
- Key attributes preview with checkmarks for confirmed items
- Balanced action buttons (approve vs edit)
- Expandable sections for additional detail without overwhelming

#### Tier 3: Detailed Review (<70% confidence)
```
┌─────────────────────────────┐
│ 🔴 Needs attention 65%      │
├─────────────────────────────┤
│ [Images] [Content] [Details]│ ← Tab navigation
│                             │
│ Issues found:               │
│ • Category uncertain        │
│ • Brand not detected        │
│ • Size needs confirmation   │
│                             │
│ For detailed editing,       │
│ visit desktop version       │
│                             │
│ [Continue Mobile] [Got it]  │
└─────────────────────────────┘
```

**Key Features:**
- Clear problem identification with specific issues listed
- Tab-based organization for complex information
- Gentle suggestion for desktop use without blocking mobile workflow
- Option to continue with mobile editing despite complexity

**Interaction Notes:** Swipe gestures for image comparison, single-tap approval

**Design File Reference:** figma-mobile-tier1-review.fig

### Mobile Edit Interface

**Purpose:** Comprehensive editing capabilities within mobile constraints

```
┌─────────────────────────────┐
│ Edit Details                │
├─────────────────────────────┤
│ Your Prompt:                │
│ ┌─────────────────────────┐ │
│ │Nike shoes 42 new       │ │
│ └─────────────────────────┘ │
│ [Update & Regenerate]       │
│                             │
│ Title:                      │
│ ┌─────────────────────────┐ │
│ │Nike Air Max Running... │ │
│ └─────────────────────────┘ │
│                             │
│ Category: Shoes > Athletic  │
│ [Change Category]           │
│                             │
│ Size: [42 ▼] Color: [Black▼]│
│ Condition: [New ▼]          │
│                             │
│ Description:                │
│ ┌─────────────────────────┐ │
│ │Zapatillas ideales para  │ │
│ │running. Diseño moderno..│ │
│ └─────────────────────────┘ │
│                             │
│ [Save Changes] [Cancel]     │
└─────────────────────────────┘
```

**Editing Capabilities:**
- **Prompt editing:** Full text field with regeneration trigger
- **Title editing:** Direct text input with character limits
- **Category selection:** Mobile-optimized picker interface
- **Key attributes:** Dropdown selectors for size, color, condition, brand
- **Description editing:** Multi-line text area for basic description editing
- **Regeneration:** "Update & Regenerate" button triggers AI reprocessing

**Interaction Notes:** Form-based editing with real-time validation and auto-save

**Design File Reference:** figma-mobile-edit.fig

### Desktop Product Management

**Purpose:** Advanced editing and image management hub

```
┌─────────────────────────────────────────────────────────────────┐
│ Nike Running Shoes - Complete Management                  [Save] │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ YOUR INPUTS                  │ │ AI GENERATED RESULTS        │ │
│ │                              │ │                             │ │
│ │ 📷 YOUR PHOTOS:              │ │ 🖼️ PROCESSED IMAGES:       │ │
│ │ [🖼️][🖼️][🖼️][🖼️] [+ Add]   │ │ [🖼️][🖼️][🖼️][🖼️]        │ │
│ │ [Delete] [Reorder]           │ │ Main for ML: [🖼️] ⭐        │ │
│ │                              │ │ [Choose Different Main]      │ │
│ │ 📝 YOUR PROMPT:              │ │                             │ │
│ │ ┌──────────────────────────┐ │ │ 📝 GENERATED CONTENT:       │ │
│ │ │"Nike shoes 42 new"      │ │ │ Title: Nike Air Max...      │ │
│ │ └──────────────────────────┘ │ │ Category: Shoes > Athletic  │ │
│ │                              │ │ Attributes: Brand: Nike...  │ │
│ │                              │ │ Description: Zapatillas...  │ │
│ │                              │ │                             │ │
│ │                              │ │ 📊 CONFIDENCE:              │ │
│ │                              │ │ Overall: 🟡 78%             │ │
│ │                              │ │ • Images: 94% ✓             │ │
│ │                              │ │ • Title: 87% ✓              │ │
│ │                              │ │ • Category: 78% ⚠           │ │
│ │                              │ │ • Attributes: 65% ⚠         │ │
│ │                              │ │                             │ │
│ │ 🔍 COMPARISON:               │ │ 📱 ML PREVIEW:              │ │
│ │ Original ←→ Enhanced         │ │ [Preview as listing]        │ │
│ │ [View Before/After]          │ │ [Publish to MercadoLibre]   │ │
│ └──────────────────────────────┘ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Full CRUD Capabilities:**
- **Add Images:** Drag & drop or file browser upload
- **Delete Images:** Individual image removal with confirmation
- **Reorder Images:** Drag to reorder image sequence
- **Main Selection:** Choose which processed image goes to MercadoLibre
- **Comparison View:** Before/after slider for quality assessment

**Auto-Processing Behavior:**
- Adding new image → Automatically processes and regenerates content
- Editing prompt → Automatically regenerates content based on new context
- Deleting image → Reprocesses remaining images and updates content
- No manual "reprocess" buttons needed - everything is automatic

**Interaction Notes:** Mouse-based interactions with hover states, drag-and-drop for image management

**Design File Reference:** figma-desktop-management.fig

### Desktop Dashboard

**Purpose:** Comprehensive product overview with advanced filtering and management

```
┌─────────────────────────────────────────────────────────────────┐
│ IntelliPost AI                                   Search: [     ] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [📷 Add New Product]            Filters: [All] [Ready] [Draft] │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Status │ Product        │ Category     │ Confidence │ Actions││
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 🟢     │ Nike Shoes     │ Sneakers     │ 92%        │ [Pub] ││
│ │        │ Size 42, New   │              │            │ [Edit]││
│ │                                                                 │
│ │ 🟡     │ iPhone Case    │ Electronics  │ 78%        │ [Rev] ││
│ │        │ Clear, Silicone│              │            │ [Edit]││
│ │                                                                 │
│ │ 🔴     │ Laptop Stand   │ Accessories  │ 65%        │ [Fix] ││
│ │        │ Adjustable     │              │            │ [Edit]││
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Search and Filter:** Find products by name, status, or category
- **Sortable Columns:** Sort by confidence, date, status, etc.
- **Bulk Actions:** Select multiple products for batch operations (post-MVP)
- **Status Overview:** Quick visual assessment of product readiness

**Interaction Notes:** Standard desktop patterns with keyboard shortcuts for power users

**Design File Reference:** figma-desktop-dashboard.fig
