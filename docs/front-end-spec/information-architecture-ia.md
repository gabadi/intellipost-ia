# Information Architecture (IA)

## Site Map / Screen Inventory

```mermaid
graph TD
    A[Login] --> B[Dashboard]
    B --> C[Add New Product]
    B --> D[Product Management]
    B --> E[Settings/Credentials]
    
    C --> C1[Image Upload]
    C1 --> C2[Processing Status]
    C2 --> C3[Review Screen]
    
    C3 --> C4[Quick Approval - Tier 1]
    C3 --> C5[Balanced Review - Tier 2]
    C3 --> C6[Detailed Review - Tier 3]
    
    C4 --> C7[Publish Confirmation]
    C5 --> C8[Edit Interface]
    C6 --> C9[Desktop Suggestion]
    
    C8 --> C7
    C9 --> C7
    
    D --> D1[Product List]
    D1 --> D2[Individual Product View]
    D2 --> D3[Desktop Image Management]
    D2 --> D4[Desktop Content Editor]
    
    E --> E1[MercadoLibre Credentials]
    E --> E2[Automation Settings]
```

## Navigation Structure

**Primary Navigation:** 
- Mobile: Bottom navigation bar with Dashboard, Add Product, and Settings
- Desktop: Top navigation bar with Dashboard, Products, and Settings

**Secondary Navigation:** 
- Mobile: Contextual navigation within workflows (Back, Next, Edit)
- Desktop: Sidebar navigation for product management functions

**Breadcrumb Strategy:** 
- Mobile: Minimal breadcrumbs, focus on contextual back buttons
- Desktop: Full breadcrumb trail for complex workflows
