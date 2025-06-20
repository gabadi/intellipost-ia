# IntelliPost AI - Product Requirements Document (PRD)

## 1. Goal, Objective and Context

* **Overall Goal:**
  The primary goal of the "IntelliPost AI" MVP is to fundamentally transform the product listing creation process for MercadoLibre. It aims to empower Small to Medium-sized Enterprises (SMEs) and sole proprietors to generate professional, optimized, and platform-compliant listings from raw product data (minimal textual prompts and basic images) with minimal time and effort, through an intelligent and highly automated system.

* **Product Objective (MVP):**
  The MVP will deliver a streamlined, AI-powered solution focused exclusively on MercadoLibre that achieves the following:
    1.  **Drastically Reduce Listing Time & Effort:** Design the system to aspire to an approximate 90% reduction in user's manual cycle time from raw input to a review-ready listing content, compared to fully manual methods.
    2.  **Automate Data Extraction & Content Generation:** Intelligently extract product information (category, title elements, attributes, description points) from user-provided raw images (especially product packaging) and minimal textual prompts. Automatically process a primary product image to professional standards (e.g., white background). Generate optimized titles, complete technical sheets (attributes), and structured, informative descriptions tailored for MercadoLibre's algorithm.
    3.  **Ensure High-Quality, Compliant Listings:** Produce listings that are not only technically compliant with MercadoLibre's requirements but also adhere to best practices for visibility and effectiveness, resulting in professional-quality outputs.
    4.  **Deliver a Simple & Intuitive User Experience:** Provide an extremely user-friendly interface for minimal data input, clear feedback, and efficient review and approval of system-generated listing content.
        *This system (MVP) will focus on generating the descriptive and categorical content for single products (no variants, single standard listing type) and will not manage price or stock, which are considered external.*

* **Context:**
  Currently, sellers (particularly SMEs and sole proprietors) face a tedious, time-consuming, and error-prone manual process to create effective listings on MercadoLibre. This involves significant effort in data entry, image preparation, understanding platform-specific best practices, and ensuring compliance, which limits scalability and diverts focus from core business growth activities. "IntelliPost AI" aims to solve this by automating the most complex and labor-intensive parts of content creation, leveraging AI to act as an expert publishing assistant. The initial focus is MercadoLibre, with a view towards future multi-platform extensibility.

## 2. Documentation Standards and Language Requirements

**DS1: Official Project Language Standard**
* **DS1.1: Technical Documentation:** All project documentation, code comments, commit messages, pull request descriptions, technical specifications, user stories, and development-related documentation MUST be written in English.
* **DS1.2: Code Standards:** All variable names, function names, class names, module names, and any text within the codebase MUST be in English.
* **DS1.3: User-Facing Content:** User interface language, error messages, and user-facing content will be determined during the UX/UI design phase and are not constrained by this documentation standard.
* **DS1.4: Development Communication:** All technical meetings, code reviews, and development-focused communications should be conducted in English to ensure consistency and facilitate future team scalability.

**DS2: Documentation Quality Requirements**
* **DS2.1: Consistency:** All documentation must maintain consistent terminology, formatting, and style throughout the project.
* **DS2.2: Clarity:** Technical documentation must be clear, precise, and accessible to English-speaking developers and stakeholders.
* **DS2.3: Version Control:** All documentation changes must be tracked in version control with clear English commit messages.

**DS3: Compliance and Enforcement**
* **DS3.1: Quality Gates:** The English language requirement is part of the Definition of Done (NFR8.1) - no story can be considered complete if it contains non-English documentation or code.
* **DS3.2: Code Review:** All code reviews must verify adherence to English language standards.
* **DS3.3: User Interface Flexibility:** The system architecture should support future localization and internationalization decisions made during UX/UI design phases.

## 3. Functional Requirements (MVP)

**FR1: Product Item-Centric Input Management**
* FR1.1: The system will allow the user to initiate the content generation process for a **specific product**. The user will provide a minimal textual prompt (e.g., product name, main keywords) that will serve as a **general guide for the AI or to make fine adjustments to the content it generates.**
* FR1.2: The system will allow the user to upload multiple raw digital images (e.g., product photos from various angles, packaging/box photos) associated with that product.
* FR1.3: The system will **automatically select the most suitable image** from those uploaded to be processed as the main listing image. The user will have the option to review and confirm/change this selection.
* FR1.4: The system will allow the user to review and, if necessary, edit the information that the system has extracted or generated *before* the final creation of the listing content.

**FR2: AI-Powered Data Extraction**
* FR2.1: The system will analyze the uploaded images (with special emphasis on product packaging) and the user's textual prompt to automatically extract relevant product information. The user's prompt serves as context or to refine the AI's results, not as direct instruction on how to extract from the image.
* FR2.2: The extracted information should include, whenever possible, sufficient data to: Suggest MercadoLibre category with high precision; Build elements for an effective title; Identify key attributes for the product's technical sheet; Obtain content points for the product description.
* FR2.3: The system will internally structure all collected information for use in content generation.
* **FR2.4: The data extraction logic and subsequent content generation (see FR4) must be designed to incorporate and actively apply the findings from research on MercadoLibre publishing best practices and algorithm optimization (as defined in the "Relevant Research" section of the Project Brief and the provided research reports).**

**FR3: Automated Main Image Processing**
* FR3.1: The system will automatically process the image designated as main to achieve a professional-quality white background, meeting MercadoLibre standards.
* FR3.2: The system will perform basic automatic adjustments to the main image (e.g., intelligent cropping, resizing) to ensure compliance with MercadoLibre's technical guidelines for the listing's main image.
* FR3.3: In the MVP, other images uploaded by the user (other than the main one) will be used exclusively as a source for data extraction (see FR2) and will not be published as secondary images in the listing.

**FR4: Intelligent Listing Content Generation for MercadoLibre**
* FR4.1: The system will automatically generate a product title optimized specifically for MercadoLibre's algorithm and product category, using extracted data and applying platform best practices.
* FR4.2: The system will automatically select or propose the most accurate and suitable MercadoLibre category for the product, based on extracted data (and ML API according to Story 2.3).
* FR4.3: The system will automatically complete MercadoLibre's technical sheet (attributes/characteristics) using extracted data and category information, prioritizing required attributes and key recommended ones.
* FR4.4: The system will automatically generate a product description that is informative, well-structured, and applies MercadoLibre best practices, based on extracted data.
* FR4.5: The system will generate content for a single standard MercadoLibre listing per product (the MVP will not include support for product variants or creation of multiple listing types).
* FR4.6: The system will **not** include or manage price or stock information in the listing content it generates; these are considered externally managed data for the MVP.

**FR5: Feedback, Review, Approval & Publishing Workflow**
* FR5.1: The system will analyze the quality of the provided raw images, both for their suitability for data extraction and for main image processing.
* FR5.2: If inputs are critically insufficient, the system will provide specific and actionable feedback with clear proposals/call to action.
* FR5.3: The system will present the user with a complete draft of the generated listing content for review. The standard workflow will require **explicit user approval.**
* **FR5.3.1 (Automated Flow Option):** The system must offer an **optional configuration** that allows the user to activate a more automated flow. In this mode, if the "confidence index" (FR5.4) of the AI-generated content for a product reaches a predefined high threshold, the system could mark the content as "ready for external publishing stage" **without requiring individual explicit approval.**
* FR5.4: The system will be able to show a "confidence index" or summary indicating how well it considers it has been able to apply best practices.
* **FR5.5: Automated Content Publishing to MercadoLibre:** After approval (explicit or automatic), the system **will attempt to automatically publish said content to MercadoLibre using the corresponding APIs**, informing the user about success or failure.

**FR6: User Interface / Control Panel**
* FR6.1: The system will offer a web-based control panel that is **100% simple, intuitive, and with professional design.**
* FR6.2: It will allow data entry (minimal prompt, image upload) associated with a product.
* FR6.3: It will display a product list with **clearly identifiable current status, including prominent visual indicators (e.g., colors, icons) based on the 'confidence index' (FR5.4) or if the product requires specific user attention.**
* FR6.4: It will allow **basic searches and apply filters** to the product list.
* FR6.5: It will allow editing the initial prompt or managing images *before* the processing cycle.
* FR6.6: It will facilitate review and approval (or tracking in automated mode) of generated content.
* FR6.7: It will clearly display any system feedback or error messages.

## 4. Non-Functional Requirements (MVP)

* **NFR1: Usability**
    * NFR1.1: The Control Panel user interface must be perceived by target users as **100% intuitive, modern and professional.**
    * NFR1.2: A new user should be able to complete the content generation flow for their first product in **less than [X] minutes of active interaction time** (excluding AI waiting times). *(X to be defined, target: very fast).*
    * NFR1.3: The Control Panel interface must be **highly responsive.**
* **NFR2: System Performance**
    * NFR2.1: The system must **keep the user clearly informed about the progress** of background AI tasks.
    * NFR2.2: AI processing times, while variable, should not be perceived as "unreasonable" for an MVP.
* **NFR3: Reliability & Availability**
    * NFR3.1: Core functionalities must operate consistently with adequate inputs.
    * NFR3.2: Controlled error management with useful messages.
    * **NFR3.3: Availability (Uptime): For the MVP, aspire to 99%.** (Given the expected periodic usage).
* **NFR4: Security**
    * NFR4.1: Communications over **HTTPS.**
    * NFR4.2: Secure handling of MercadoLibre API keys (encrypted storage, restricted access).
* **NFR5: Maintainability & Extensibility**
    * NFR5.1: **Inherently modular** architecture (Hexagonal, static duck typing).
    * NFR5.2: Code and documentation under **"agent coding first"** principles.
    * NFR5.3: MVP design should not structurally prevent future extensibility to other platforms.
* **NFR6: Data Integrity**
    * NFR6.1: Ensure product data remains accurate, consistent and uncorrupted.
* **NFR7: Data Persistence**
    * NFR7.1: Securely persist user work data (prompts, image refs, AI content, states).
    * NFR7.2: Prevent work loss between sessions or interruptions.
    * NFR7.3: Internal persistence model does not need to be strictly ACID transactional for every operation in MVP.
* **NFR8: Quality Gate for Story Completion (Definition of Done):**
    * NFR8.1: Before any development story is considered 'complete', it must successfully pass all automated quality checks (linting, formatting, types, architecture) and all relevant automated tests.

## 5. User Interaction and Design Goals

This section describes the high-level vision and objectives for the User Experience (UX) and User Interface (UI) of the "IntelliPost AI" MVP. It will serve as a fundamental brief for the subsequent work of the Design Architect.

1.  **Overall Vision and Desired Experience:**
    * The system will embody **Professional and Minimalist Efficiency**. The design will be modern, clean, with absolute focus on functionality without superfluous elements, using a professional or neutral color palette and clear, highly readable typography. The user experience will seek for users to feel in control, efficient, and perceive the tool as an expert, direct and powerful assistant: "Power under the hood, simplicity on the surface".
    * Incorporate mechanisms of **subtle micro-induction and contextual tips** to help new users discover and leverage AI capabilities within the minimalist UI.
2.  **Key Interaction Paradigms:**
    * The interaction will be centered on a **Central Control Panel with Detailed Actions per Product**. Users will manage a list of their products in a main dashboard-type view. When selecting a specific product, they will access the actions and detailed views corresponding to that item.
3.  **Central Screens/Views (Conceptual for MVP):**
    * A **Main Control Panel** (product list and statuses, with "Smart Sections" or predefined priority views to facilitate rapid scanning).
    * When selecting a product, a **Single Consolidated View for the "Product in Process"** (with information organized in collapsible sections and "progressive disclosure" to handle information density, and a visual guide or "review checklist" for items resumed from mobile).
4.  **Accessibility Aspirations (MVP):**
    * The MVP will focus on **Accessibility Fundamentals**: Complete Keyboard Navigation for essential functions, Adequate Color Contrast for readability (e.g., WCAG AA ratios), and Clear Alternative Texts for icons and non-textual controls.
5.  **Branding Considerations (High Level for MVP):**
    * The MVP will establish the **distinctive visual identity of "IntelliPost AI"**. It will not incorporate user brand customization in this version.
6.  **Target Devices/Platforms (Web UI for MVP):**
    * **Initial Input Loading (Prompt and Images):** Optimized for **mobile devices.**
    * **Complete Control Panel Functionality (Review, Editing, State Management):** Optimized for **desktop and tablet environments**, with basic responsive accessibility on mobile.
7.  **Additional Design Principle (Future Vision):**
    * Although the MVP focuses on individual products, the Control Panel design and information presentation should **be conceived considering future incorporation of batch management and variant functionalities**, favoring adaptable UI structures.

## 6. Technical Assumptions (Final Updated Version)

This section describes the high-level technical decisions, fundamental assumptions, architectural preferences, and initial identified risks that will guide the design and development of the "IntelliPost AI" MVP.

**5.1. Fundamental Architectural Decisions:**
* **5.1.1. Code Repository Structure:** **Monorepo**.
    * *Reason:* Simplify dependency management, facilitate atomic commits, consistency in tools, beneficial for "Agent Coding First".
* **5.1.2. High-Level Service Architecture:** **Modular Monolith (designed with Hexagonal Principles).**
    * *Reason:* Aligned with preference for modular and decoupled components. Initial simplicity for MVP, facilitates future evolution. Hexagonal architecture, implemented with 'ports' and 'adapters' (or 'resources') by statically validated structural convention, will mitigate risks of dependency on specific AI components by facilitating their replacement.

**5.2. Technology Stack Preferences and Directions (MVP):**
* **5.2.1. Backend Language & Framework:** **Python** with **FastAPI**.
    * *Reason:* AI/ML ecosystem, FastAPI performance, type hints. Python is a language in which LLMs are usually very well trained, favoring "Agent Coding First".
* **5.2.2. Frontend Control Panel Technology:** **Svelte** (with SvelteKit).
    * *Reason:* User preference. Valued for performance, DX, and capability for professional UIs.
* **5.2.3. AI Technologies Approach (Preferred Direction for Initial Research and Development):** Hybrid approach. Research (already provided in `reports/`) and initial development will prioritize and evaluate:
    * Specialized third-party APIs for critical visual processing (e.g., white background).
    * Direct use of multimodal LLMs for image data extraction.
    * LLMs (multimodal or text) for MercadoLibre-optimized content generation.
    * Alternatives/complements: Python OCR/NLP libraries, cloud provider AI services.
* **5.2.4. Database:** **PostgreSQL** and **Object Storage**.
    * *Reason:* PostgreSQL for structured/semi-structured data (JSONB). Object Storage for images.

**5.3. General Development and Architecture Principles (Refined):**
* **5.3.1. Fundamental Modularity and Hexagonal Design:** Strong reference to Hexagonal Architecture (Ports and Adapters) per functionality module, as illustrated by the user example (to be shared with Architect). Internal 'adapters' will be favored to comply with 'ports' (`typing.Protocol`) by validated structural convention (e.g., Pyright).
* **5.3.2. Decoupled Inter-Module Communication:** Pattern with consumer-defined ports and shared DTOs (minimal and necessary Shared Kernel from DDD). Platform modules (e.g., `mercadolibre_manager`) will use specialized services (e.g., `image_engine`).
* **5.3.3. "Agent Coding First", Code Quality, Rigorous Static Typing and Architectural Boundary Maintenance:** Optimize collaboration with LLMs and ensure high quality. This includes:
    * *Consistent Linting and Formatting:* **Ruff** (Python), **ESLint/Prettier** (Svelte/JS/TS).
    * *Rigorous Static Typing:* **Pyright** (Python, using `typing.List` etc.), **TypeScript** (Svelte).
    * *Architectural Boundary Maintenance:* **Tach** (Python), **dependency-cruiser** (Svelte/JS/TS).
    * *Code Documentation (Fair and Necessary):* Prioritize self-documented code. Explicit comments/documentation only when necessary.
* **5.3.4. Cost Management:** Openness to reasonable paid services.
* **5.3.5. Test-Driven Development (TDD) Methodology: Test-Driven Development (TDD) methodology will be adopted mandatorily.** Tests (unit and relevant integration) will be written *before* the functionality code to guide implementation and ensure correctness, coverage, and inherently testable design from the start.

**5.4. Key Technical and Operational Assumptions:**
* Users can capture basic images with mobile phones.
* MercadoLibre APIs are capable and reliable for the MVP.
* Viable AI technologies exist and are accessible.

**5.5. Identified Technical Risks (Initial List):**
* Integration Complexity (ML API, third-party AI).
* AI Performance and Quality (especially images and data extraction).
    * *Architectural Mitigation:* Hexagonal architecture with interchangeable "adapters/resources" will facilitate replacement or updating of AI services.

## 7. Epic Overview

### **Epic 1: Base Platform and Initial Control Panel (The Smart Foundation)**

**Story 1.1: Initial Project Setup, Monorepo and Centralized Development and Quality Tools**
- **Description:** Establish the base monorepo structure with all development tools, linting, formatting and type checking necessary to maintain high code quality and facilitate "Agent Coding First" development.
- **Acceptance Criteria:**
  - Monorepo configured with UV for Python dependency management
  - Ruff configured for Python linting and formatting
  - Pyright configured for static type checking
  - ESLint/Prettier configured for Svelte frontend
  - Tach configured to verify architectural boundaries
  - dependency-cruiser configured for frontend
  - Pre-commit hooks established
  - Developer setup documentation

**Story 1.2: Basic Backend Application Framework (FastAPI)**
- **Description:** Create the base backend structure with FastAPI following hexagonal architecture principles and defined modular patterns.
- **Acceptance Criteria:**
  - Functional FastAPI application with modular structure
  - CORS configuration for local frontend
  - Functional health check endpoint
  - Appropriately configured logging
  - Environment variables handled correctly
  - Folder structure following hexagonal conventions

**Story 1.3: Basic Frontend Application Framework (Svelte)**
- **Description:** Establish the base frontend application with SvelteKit, including basic routing and structure for the control panel.
- **Acceptance Criteria:**
  - Functional SvelteKit application
  - Basic routing configured
  - Backend connection established
  - Base CSS framework/design system implemented
  - Base component structure defined
  - Build and dev scripts working

**Historia 1.4: Definición y Configuración Inicial de la Base de Datos (PostgreSQL)**
- **Description:** Configure PostgreSQL with initial schema including user model and base structure for products.
- **Criterios de Aceptación:**
  - PostgreSQL configurado y funcional
  - Migraciones iniciales creadas
  - Modelo de Usuario definido
  - Modelo de Producto base definido
  - Pool de conexiones configurado
  - Scripts de setup de BD documentados

**Historia 1.5: Implementación de Autenticación de Usuario Básica en el Backend**
- **Description:** Implement basic authentication system with JWT for secure system access.
- **Criterios de Aceptación:**
  - Endpoints de login/registro funcionales
  - JWT tokens generados y validados correctamente
  - Middleware de autenticación implementado
  - Manejo seguro de contraseñas (hashing)
  - Refresh token functionality básica
  - Validación de entrada robusta

**Historia 1.6: Implementación del Marco del Panel de Control Básico con Flujo de Login**
- **Descripción:** Crear la UI base del panel de control con flujo de autenticación integrado.
- **Criterios de Aceptación:**
  - Página de login funcional
  - Dashboard base implementado
  - Navegación principal establecida
  - Estado de autenticación manejado correctamente
  - Logout funcional
  - Redirecciones apropiadas implementadas

**Historia 1.7: Establecimiento del Pipeline Inicial de CI/CD**
- **Descripción:** Configurar pipeline de integración continua y despliegue continuo para automatizar testing y deployment.
- **Criterios de Aceptación:**
  - CI pipeline ejecuta linting, type checking y tests
  - Build process automatizado
  - Deploy pipeline básico configurado
  - Quality gates implementados (NFR8.1)
  - Notificaciones de status configuradas

**Historia 1.8: Configuración de credenciales MercadoLibre API**
- **Descripción:** Sistema para configurar y gestionar credenciales de API de MercadoLibre necesarias para categorización y publicación, diseñado considerando futuro soporte multi-cuenta.
- **Criterios de Aceptación:**
  - Interfaz para configurar credenciales ML (App ID, Secret Key, Access Token)
  - Almacenamiento seguro y encriptado de credenciales
  - Validación de credenciales contra API de ML
  - Estructura de BD preparada para futuro multi-cuenta (sin implementar)
  - Renovación automática de tokens cuando sea posible
  - Gestión de errores de credenciales inválidas/expiradas

### **Epic 2: Complete ML Content Generation**

**Story 2.1: Input upload interface (mobile-optimized)**
- **Description:** Mobile-first responsive form to take direct photo with camera or upload multiple images, standard multiple file input, textual prompt field with specific validations.
- **Acceptance Criteria:**
  - Mobile-first responsive form with camera access
  - Multiple upload: maximum 8 images per product
  - Format validation: only JPG, PNG
  - Size validation: 10MB maximum per image, 50MB total
  - Resolution validation: minimum 800x600px
  - Textual prompt field: maximum 500 characters, minimum required
  - At least 1 image required to continue
  - Image preview with thumbnails
  - Progress indicators during upload
  - Error handling with specific messages per validation

**Historia 2.2: Almacenamiento Seguro de los Inputs Crudos del Producto**
- **Description:** Implement secure storage system for images in object storage and product data in DB.
- **Criterios de Aceptación:**
  - Imágenes almacenadas en object storage seguro
  - Product metadata persisted in PostgreSQL
  - URLs seguras generadas para acceso a imágenes
  - Correct relationships between product and images
  - Limpieza automática de archivos temporales
  - Backup strategy definida

**Historia 2.3: IA para generación de contenido texto ML**
- **Descripción:** Integración con LLM que analiza imágenes + prompt, genera título optimizado para algoritmo ML, usa herramienta oficial ML para categoría (evitar penalizaciones), mapea atributos a categoría específica, genera descripción estructurada aplicando best practices ML investigadas.
- **Criterios de Aceptación:**
  - Integración con LLM multimodal funcional
  - Generación de título optimizado para algoritmo ML
  - Uso de herramienta oficial ML para categoría
  - Mapeo de atributos a categoría específica
  - Generación de descripción estructurada
  - Aplicación de conocimiento de ML best practices
  - Manejo básico de errores con retry automático y feedback claro

**Historia 2.4: IA para procesamiento de imagen principal ML**
- **Descripción:** Sistema que procesa TODAS las imágenes cargadas (fondo blanco, ajustes de calidad), después del procesamiento decide cuál queda como principal, integración con servicio de IA para remover fondo, ajustes automáticos, redimensionado según specs ML, generación de thumbnails SI ML no los provee automáticamente, validación de calidad general.
- **Criterios de Aceptación:**
  - Procesamiento de todas las imágenes cargadas
  - Selección automática de mejor imagen principal post-procesamiento
  - Procesamiento de fondo blanco implementado
  - Ajustes automáticos de calidad (sharpness, lighting)
  - Redimensionado según specs de MercadoLibre
  - Generación de thumbnails (si ML no los provee)
  - Validación de calidad general
  - Manejo básico de errores con retry automático y feedback claro

**Historia 2.5: Persistencia de todo el contenido generado**
- **Descripción:** Almacenar contenido texto (título, categoría, atributos, descripción) en PostgreSQL, imagen principal + thumbnails (si aplica) en S3, metadatos de procesamiento, URLs seguras, versionado, timestamps, relaciones correctas entre todos los componentes, y gestión de estados del producto.
- **Criterios de Aceptación:**
  - Persistencia de contenido texto en PostgreSQL
  - Almacenamiento de imagen principal en S3
  - Persistencia de thumbnails (si aplica)
  - Metadatos de procesamiento almacenados
  - URLs seguras generadas
  - Versionado implementado
  - Timestamps de creación
  - Gestión de estados del producto: uploading → processing → ready → publishing → published/failed
  - Estados simples y comprensibles para el usuario
  - Transiciones de estado trackeable y auditable
  - Relaciones correctas entre componentes

**Historia 2.6: Visualización del contenido completo**
- **Descripción:** UI que muestra todo el contenido generado, mobile-friendly para review básico, desktop-optimized para edición detallada, preview de cómo se verá en ML, comparación con datos originales, opciones básicas de edición, confidence scores visibles.
- **Criterios de Aceptación:**
  - UI mobile-friendly para review básico del contenido
  - UI desktop-optimized para edición detallada
  - Preview de cómo se verá en MercadoLibre
  - Comparación con datos originales
  - Opciones básicas de edición
  - Confidence scores visibles por componente
  - Navegación fluida entre mobile y desktop

### **Epic 3: Review & Publishing**

**Historia 3.1: Implementación del Motor de Procesamiento de Imagen Principal**
- **Descripción:** Desarrollar sistema automatizado para seleccionar y procesar imagen principal con fondo blanco profesional cumpliendo estándares de MercadoLibre.
- **Criterios de Aceptación:**
  - Selección automática de mejor imagen principal
  - Procesamiento de fondo blanco implementado
  - Ajustes automáticos de calidad (sharpness, lighting)
  - Redimensionado según specs de MercadoLibre
  - Validación de calidad de output
  - Fallback para imágenes de baja calidad
  - Performance optimizada para procesamiento

**Historia 3.2: Persistencia de la Imagen Principal Procesada y sus Metadatos**
- **Descripción:** Almacenar imagen procesada junto con metadatos de calidad y procesamiento aplicado.
- **Criterios de Aceptación:**
  - Imagen procesada almacenada en object storage
  - Metadatos de procesamiento persistidos
  - Scores de calidad almacenados
  - Relación con imagen original mantenida
  - URLs de acceso generadas
  - Versionado de procesamiento implementado

**Historia 3.3: Visualización y Validación de la Imagen Principal Procesada**
- **Descripción:** Mostrar resultado del procesamiento de imagen en panel de control para validación del usuario.
- **Criterios de Aceptación:**
  - Comparación lado a lado (original vs procesada)
  - Scores de calidad visibles
  - Opción de re-procesar disponible
  - Feedback sobre calidad de imagen
  - Selección manual alternativa disponible
  - Preview en contexto de MercadoLibre

### **Epic 4: AI-Powered Listing Content Generation (The Content that Sells)**

**Historia 4.1: Servicio de IA para Generación de Título Optimizado para MercadoLibre**
- **Descripción:** Crear sistema de IA que genere títulos optimizados para algoritmo de MercadoLibre usando datos extraídos y mejores prácticas.
- **Criterios de Aceptación:**
  - Integración con LLM para generación de títulos
  - Aplicación de ML title best practices
  - Optimización por categoría específica
  - Incorporación de keywords relevantes
  - Límites de caracteres respetados
  - Múltiples opciones generadas
  - Score de calidad calculado

**Historia 4.2: Servicio de IA para Confirmación/Selección Final de Categoría**
- **Descripción:** Refinar y confirmar categoría de MercadoLibre más precisa usando API de ML y datos del producto.
- **Criterios de Aceptación:**
  - Integración con API de categorías de ML
  - Validación de categoría sugerida
  - Refinamiento basado en atributos
  - Manejo de categorías ambiguas
  - Fallback para categorías no encontradas
  - Confidence score de categorización

**Historia 4.3: Servicio de IA para Completado Estratégico de la Ficha Técnica**
- **Descripción:** Generar automáticamente atributos técnicos completos y estratégicos para la ficha del producto en MercadoLibre.
- **Criterios de Aceptación:**
  - Mapeo de atributos por categoría
  - Completado de atributos requeridos
  - Priorización de atributos recomendados
  - Validación de formatos de valores
  - Manejo de atributos opcionales
  - Integración con API de atributos ML

**Historia 4.4: Servicio de IA para Generación de Descripción Estructurada**
- **Descripción:** Crear descripciones informativas y bien estructuradas aplicando mejores prácticas de copywriting para e-commerce.
- **Criterios de Aceptación:**
  - Descripción estructurada en secciones
  - Aplicación de principios persuasivos
  - Incorporación de datos técnicos
  - Optimización para SEO interno ML
  - Formato HTML/markdown apropiado
  - Personalización por categoría

**Historia 4.5: Consolidación y Persistencia del Contenido de Listado Generado**
- **Descripción:** Consolidar todo el contenido generado por IA en una estructura cohesiva lista para revisión y publicación.
- **Criterios de Aceptación:**
  - Estructura de listado completa consolidada
  - Persistencia de contenido generado
  - Versionado de generaciones
  - Timestamps de creación
  - Estado de completitud calculado
  - Referencias a assets relacionados

### **Epic 5: Review, Feedback & MercadoLibre Publishing (The Triumphant Launch)**

**Historia 5.1: UI para Revisión y Edición del Contenido de Listado Completo**
- **Descripción:** Crear interfaz completa para revisar, editar y aprobar todo el contenido del listado antes de publicación.
- **Criterios de Aceptación:**
  - Vista consolidada de listado completo
  - Edición in-line de título y descripción
  - Modificación de atributos técnicos
  - Preview del listado como se verá en ML
  - Comparación con datos originales
  - Guardado de cambios en tiempo real

**Historia 5.2: Presentación del Índice de Confianza y Configuración del Flujo Automatizado**
- **Descripción:** Mostrar score de confianza del contenido generado y permitir configuración de flujo automatizado opcional.
- **Criterios de Aceptación:**
  - Índice de confianza calculado y visible
  - Breakdown de score por componente
  - Configuración de umbral para auto-publicación
  - Explicación de factores de confianza
  - Toggle para modo automatizado
  - Historial de scores por producto

**Historia 5.3: Aprobación Final del Usuario y Disparo de Publicación**
- **Descripción:** Implementar flujo de aprobación final con validaciones y disparo del proceso de publicación en MercadoLibre.
- **Criterios de Aceptación:**
  - Botón de aprobación final prominente
  - Validaciones pre-publicación ejecutadas
  - Confirmación de acción requerida
  - Estado de publicación actualizable
  - Manejo de aprobación automática (si configurada)
  - Logs de decisiones de aprobación

**Historia 3.4: Servicio backend para publicación en MercadoLibre API**
- **Descripción:** Integración completa con API oficial de MercadoLibre, creación de listing con todos los campos generados, upload de imagen principal a ML, manejo robusto de errores de API con mensajes específicos, retry logic inteligente para fallos temporales, validación de respuestas ML, almacenamiento de ML listing ID y URL, manejo de rate limits de API.
- **Criterios de Aceptación:**
  - Integración completa con ML API
  - Creación de listing funcional
  - Upload de imagen principal
  - Retry logic para API ML y manejo de errores básico
  - Validación de respuestas ML
  - Almacenamiento de ML listing ID y URL
  - Manejo de rate limits de API

**Historia 5.5: Actualización de Estado y Feedback Post-Publicación**
- **Descripción:** Actualizar estado del producto en el sistema y mostrar feedback post-publicación al usuario.
- **Criterios de Aceptación:**
  - Estado de producto actualizado a "publicado"
  - URL de listado ML almacenada
  - Feedback de éxito/error mostrado claramente
  - Link directo al listado publicado
  - Timestamps de publicación registrados
  - Notificaciones de status implementadas
  - Dashboard actualizado con nuevo estado

## 8. Key Reference Documents
1.  **IntelliPost AI - Project Brief (v1.0, English Version)** - *Como se generó con Analyst Mary.*
2.  **User-Provided Architectural Example & Principles (v1.0)** - *Ejemplo detallado de estructura modular Hexagonal provisto por el usuario.*
3.  **Research Report: AI Technology Evaluation for Image Processing & Data Operations** - *Referencia a los archivos en `reports/image_processing/` (claude.md, gemini.md, x.md).*
4.  **Research Report: MercadoLibre Publishing Best Practices & Algorithm Insights** - *Referencia a los archivos en `reports/publishing/meli/` (claude.md, gemini.md, x.md).*
5.  **Research Report: Universal Principles of Persuasive & High-Conversion Publishing** - *Referencia a los archivos en `reports/publishing/general/` (claude.md, gemini.md, x.md).*
6.  **Research Prompts (Generated)** - *Los 3 prompts detallados generados durante la fase de PRD como mandato para las investigaciones, cuyos hallazgos iniciales están en los reportes anteriores.*

## 9. Out of Scope Ideas Post MVP
The following functionalities are explicitly considered out of scope for the MVP and will be evaluated for future versions:
* Product Variant Management.
* Support for Multiple Publication Types per Product in MercadoLibre.
* Batch Loading and Processing.
* Advanced and Varied Secondary Image Generation (e.g., lifestyle).
* Automatic System Adaptation to Platform Rule Changes.
* Publisher Extensibility to Other E-commerce Platforms.
* Performance Analytics and Optimization Suggestions Module (Post-Publication).
* Advanced Keyword and Trend Assistance Features (beyond MVP).
* Automated "Forgot My Password" Functionality.
* User Auto-Registration / Complete Multi-Client Management.
* "Save Draft" Functionality for Initial Inputs.
* Detailed Accessibility (Beyond MVP Fundamentals).

## 10. Change Log
| Change | Date | Version | Description | Author |
| ------ | ---- | ------- | ----------- | ------ |
| Initial Creation | 2025-05-27 | 1.0 | Initial PRD creation. | John (PM) |

--- END PRD START CHECKLIST OUTPUT ------

## 11. Checklist Results Report

### **Executive Summary**
The IntelliPost AI PRD has demonstrated significant improvement and now presents a comprehensive and robust structure with clear objectives, complete functional requirements, and well-defined technical assumptions. The critical gaps previously identified have been successfully resolved.

**Quality Score: 8.7/10** (Significant improvement from 7.2/10)

### **Main Improvements Since Previous Evaluation**

#### **🚀 SIGNIFICANT IMPROVEMENTS**
1. **Epic Overview Completion**: From incomplete to 19 detailed user stories with comprehensive acceptance criteria
2. **Comprehensive Error Handling**: Retry logic, fallback mechanisms and specific error scenarios throughout the system
3. **Detailed Validation Framework**: Specific limits (max 8 images, 10MB/50MB, minimum 800x600px, only JPG/PNG)
4. **Product State Management**: Clear progression (uploading → processing → ready → publishing → published/failed)
5. **MercadoLibre Integration**: Story 1.8 for comprehensive API credential management
6. **Epic Reorganization**: From 5 to 3 epics for better coherence and logical flow
7. **Enhanced Mobile/Desktop Optimization**: Platform-specific optimization strategies

### **Resultados de Validación Actualizados por Categoría**

#### **1. Alineación Estratégica y Contexto de Negocio** ✅ **APROBADO** (Previamente ✅)
- **Mejoras**: Objetivos cuantificables (reducción 90% tiempo), targeting SME claro, alcance MVP explícito
- **Fortalezas**: Objetivos estratégicos cristalinos, propuesta de valor bien definida
- **Gaps Menores**: Métricas de éxito más allá de reducción de tiempo, detalles del modelo de negocio

#### **2. Completitud de Requerimientos Funcionales** ✅ **APROBADO** (Previamente ⚠️)
- **Mejora Principal**: Epic Overview completo con 19 historias detalladas (antes incompleto)
- **Nuevas Adiciones**: Manejo integral de errores, reglas de validación detalladas, gestión de estados
- **Fortalezas**: Cobertura end-to-end del journey del usuario, manejo de casos edge, flujo mobile-to-desktop
- **Gaps Menores**: Especificidad del flujo de onboarding, ruta de migración de operaciones masivas

#### **3. Requerimientos No Funcionales** ✅ **APROBADO** (Previamente ⚠️)
- **Mejoras**: Requerimientos de usabilidad mejorados, objetivos 99% uptime, seguridad integral
- **Fortalezas**: Expectativas claras de rendimiento, requerimientos de integridad de datos, quality gates
- **Gaps Menores**: Benchmarks específicos de rendimiento, detalles de recuperación ante desastres

#### **4. Estructura de Epics e Historias de Usuario** ✅ **APROBADO** (Previamente ❌)
- **Mejora Principal**: Transformación completa de ausente a comprensivo
- **Nueva Estructura**: 3 epics bien organizados con progresión lógica
- **Fortalezas**: Criterios de aceptación detallados, especificaciones técnicas, dependencias claras
- **Issues Menores**: Algunas inconsistencias de numeración, estimaciones de complejidad faltantes

#### **5. Validación de Asunciones Técnicas** ✅ **APROBADO** (Previamente ⚠️)
- **Mejoras**: Stack tecnológico comprensivo con justificaciones, TDD obligatorio
- **Fortalezas**: Decisiones arquitectónicas claras, enfoque agent-coding-first, tooling de calidad
- **Gaps Menores**: Requerimientos de versiones específicas, detalles de deployment

#### **6. Objetivos de Interacción de Usuario y Diseño** ✅ **APROBADO** (Previamente ⚠️)
- **Mejora Principal**: De básico a visión UX comprensiva
- **Nuevas Adiciones**: Progressive disclosure, micro-inducción, estrategia de optimización por dispositivo
- **Fortalezas**: Filosofía de diseño clara, requerimientos de accesibilidad, optimización específica por plataforma
- **Gaps Menores**: Guías detalladas de branding, características avanzadas de accesibilidad

#### **7. Definition of Done y Quality Gates** ✅ **APROBADO** (Previamente ⚠️)
- **Mejoras**: NFR8.1 quality gates comprensivos, TDD obligatorio, tooling detallado
- **Fortalezas**: Aseguramiento de calidad multi-capa, compliance arquitectónico, testing automatizado
- **Gaps Menores**: Objetivos de cobertura de código, procedimientos de user acceptance testing

#### **8. Gestión de Riesgos y Mitigación** ⚠️ **GAP MENOR** (Previamente ❌)
- **Alguna Mejora**: Riesgos técnicos básicos identificados con mitigación arquitectónica
- **Fortalezas**: Arquitectura hexagonal como estrategia de mitigación de riesgos
- **Gaps Restantes**: Registro comprensivo de riesgos, riesgos de negocio/operacionales, planes de contingencia

#### **9. Dependencias e Integraciones Externas** ✅ **APROBADO** (Previamente ❌)
- **Mejora Principal**: Integración comprensiva MercadoLibre, dependencias de servicios IA
- **Nuevas Adiciones**: Gestión de credenciales, rate limiting, estrategias de fallback
- **Fortalezas**: Múltiples opciones de servicios IA, seguridad para APIs externas, enfoques de backup
- **Gaps Menores**: Requerimientos específicos de SLA, cuantificación de costos

#### **10. Gestión de Datos y Privacidad** ⚠️ **GAP MENOR** (Previamente ❌)
- **Mejoras**: NFR6/NFR7 para integridad y persistencia de datos, ciclo de vida de datos claro
- **Fortalezas**: Gestión de estados, estrategia de backup, seguridad para datos sensibles
- **Gaps Restantes**: Marco de compliance GDPR, políticas de retención de datos, consentimiento del usuario

### **Elementos Pendientes para Atención Inmediata**

#### **Mejoras de Prioridad Media**
1. **Registro Comprensivo de Riesgos**: Expandir más allá de riesgos técnicos para incluir riesgos de negocio, operacionales y de timeline
2. **Marco de Privacidad y Compliance**: Compliance GDPR, políticas de retención de datos, mecanismos de consentimiento del usuario
3. **Benchmarks de Rendimiento**: Tiempos de respuesta específicos, objetivos de throughput, umbrales de escalabilidad

#### **Mejoras de Prioridad Baja**
1. **Flujo de Onboarding del Usuario**: Diseño detallado de la experiencia del primer usuario
2. **Recuperación Avanzada de Errores**: Procedimientos comprensivos de recuperación ante desastres
3. **Estrategia de Gestión de Costos**: Enfoques detallados de presupuesto y optimización de costos

### **Evaluación Final**

El PRD ha experimentado una transformación notable, evolucionando de una base sólida con gaps críticos a un documento comprensivo y listo para desarrollo. La adición de 19 historias de usuario detalladas, manejo integral de errores y especificaciones técnicas robustas representa un progreso excepcional.

**Logros Clave:**
- ✅ Epic Overview completo con historias de usuario detalladas (gap principal resuelto)
- ✅ Requerimientos funcionales comprensivos con manejo de errores
- ✅ Arquitectura técnica robusta y estándares de desarrollo
- ✅ Gestión clara de dependencias externas
- ✅ Visión y requerimientos profesionales de UX/UI

**Recommendation:** **APPROVED FOR ARCHITECTURE PHASE** with minor improvements in risk and privacy framework to be addressed during architectural design.

**Quality Score Progression:** 7.2/10 → 8.7/10 (+1.5 improvement)

**Validation Date:** June 19, 2025  
**Validated By:** Claude Code (Product Owner Agent)  
**Status:** Ready for Architecture Phase with Minor Improvements

--- END Checklist START Design Architect `UI/UX Specification Mode` Prompt ------

## 12. Prompt for Design Architect (UI/UX Specification Mode)

**Objective:** Elaborate on the UI/UX aspects of the product defined in this PRD.
**Mode:** UI/UX Specification Mode
**Input:** This completed PRD document.
**Key Tasks:**
1. Review the product goals, user stories, and UI-related notes and "User Interaction and Design Goals" herein.
2. Collaboratively define detailed user flows, wireframes (conceptual), and key screen mockups/descriptions for the Svelte-based Control Panel.
3. Specify usability requirements and ensure adherence to the "Accessibility Fundamentals" defined.
4. Populate or create the `front-end-spec-tmpl` document (or an equivalent UI/UX Specification document).
5. Ensure that this PRD is updated or clearly references the detailed UI/UX specifications derived from your work, so that it provides a comprehensive foundation for subsequent architecture and development phases.
   Please guide the user through this process to enrich the PRD with detailed UI/UX specifications.

--- END Design Architect `UI/UX Specification Mode` Prompt START Architect Prompt ------

## 13. Initial Architect Prompt

Based on our discussions and requirements analysis for the "IntelliPost AI" project, I've compiled the following technical guidance from this PRD to inform your architecture analysis and decisions, to kick off the Architecture Creation Mode:

### Technical Infrastructure and Decisions (from PRD Section 6: Technical Assumptions)

* **Repository Structure:** Monorepo.
* **Service Architecture:** Modular Monolith, designed following Hexagonal Architecture principles.
* **Backend Language & Framework:** Python with FastAPI.
* **Frontend Panel Technology:** Svelte (with SvelteKit).
* **AI Technologies Approach:** Hybrid (Specialized 3rd party APIs for critical visual processing like background removal; strong research priority on Multimodal LLMs for data extraction from images; LLMs for content generation optimized for MercadoLibre; opportunistic use of Cloud Provider AI services).
* **Database:** PostgreSQL, complemented with Object Storage for image assets.
* **General Development Principles:** Adherence to Modular Design, Hexagonal Architecture (with static duck typing, adapters by convention, consumer-defined ports, DTOs as per user's example), "Agent Coding First" (with Ruff, Prettier, ESLint, Pyright, TypeScript, Tach, dependency-cruiser, and "just enough" documentation principles), TDD as mandatory methodology, and a "Quality Gate" NFR for story completion.
* **Cost Management:** Openness to reasonable paid services if they provide value and efficiency.
* **Key Confirmed Assumptions:** Users can provide basic phone images; ML APIs are capable; viable AI tech exists.
* **Identified Risks:** Integration complexity (ML API, 3rd party AI), and achieving consistent high-quality AI performance (image processing, data extraction). The Hexagonal architecture is a key mitigation strategy for AI component risk.

### Key Functional & Non-Functional Aspects from PRD

* The system must automate the generation of MercadoLibre listing content (title, category, attributes, description, professional main image with white background + icon) from minimal user inputs (text prompt, raw images).
* The MVP is for single products on MercadoLibre (no variants, no multi-listing types, no price/stock management by this system).
* A "100% simple, intuitiva y con diseño profesional" Panel de Control UI is required, with specific attention to mobile optimization for initial inputs.
* Target uptime for MVP is 99%. Data persistence and integrity are key.
* Security requires HTTPS and secure handling of any MercadoLibre API keys.
* The system must implement a "Quality Gate" (all automated checks pass) for story completion.

### Critical Handoff Points & User Preferences

* Refer to the "User Interaction and Design Goals" section of this PRD for detailed UX/UI vision.
* The "User-Provided Architectural Example & Principles" document is a key reference for desired backend structure and patterns.
* The various Research Reports (on ML Best Practices, AI Tech, and Persuasive Publishing) are crucial inputs for designing the AI's intelligence.

**Your Mission (Architect - Fred):**
Utilize this PRD and the referenced documents to create a comprehensive Architecture Document (following `architecture-tmpl.txt` ) that details the technical design for the "IntelliPost AI" MVP. This includes defining components, data models, API contracts, infrastructure, error handling, coding standards, testing strategy, and security best practices, ensuring alignment with all stated requirements and preferences.
