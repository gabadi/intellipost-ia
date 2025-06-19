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

## 2. Functional Requirements (MVP)

**FR1: Gestión de Inputs Centrada en el Producto (Product Item-Centric Input Management)**
* FR1.1: El sistema permitirá al usuario iniciar el proceso de generación de contenido para un **producto específico**. El usuario proporcionará un prompt textual mínimo (ej. nombre del producto, palabras clave principales) que servirá como **guía general para la IA o para realizar ajustes finos al contenido que esta genere.**
* FR1.2: El sistema permitirá al usuario cargar múltiples imágenes digitales en bruto (ej. fotos del producto desde varios ángulos, fotos del empaque/caja) asociadas a dicho producto.
* FR1.3: El sistema **seleccionará automáticamente la imagen más adecuada** de las cargadas para ser procesada como la imagen principal del listado. El usuario tendrá la opción de revisar y confirmar/cambiar esta selección.
* FR1.4: El sistema permitirá al usuario revisar y, si es necesario, editar la información que el sistema ha extraído o generado *antes* de la creación final del contenido del listado.

**FR2: Extracción de Datos Potenciada por IA (AI-Powered Data Extraction)**
* FR2.1: El sistema analizará las imágenes cargadas (con especial énfasis en el empaque del producto) y el prompt textual del usuario para extraer automáticamente información relevante del producto. El prompt del usuario sirve como contexto o para refinar el resultado de la IA, no como instrucción directa sobre cómo extraer de la imagen.
* FR2.2: La información extraída deberá incluir, siempre que sea posible, datos suficientes para: Sugerir con alta precisión la categoría de MercadoLibre; Construir elementos para un título efectivo; Identificar atributos clave para la ficha técnica del producto; Obtener puntos de contenido para la descripción del producto.
* FR2.3: El sistema estructurará internamente toda la información recopilada para su uso en la generación de contenido.
* **FR2.4: La lógica de extracción de datos y la subsecuente generación de contenido (ver FR4) deberán estar diseñadas para incorporar y aplicar activamente los hallazgos de la investigación sobre las mejores prácticas de publicación y optimización para el algoritmo de MercadoLibre (según se define en la sección "Investigación Relevante" del Project Brief y los informes de investigación provistos).**

**FR3: Procesamiento Automatizado de Imagen Principal (Automated Main Image Processing)**
* FR3.1: El sistema procesará automáticamente la imagen designada como principal para lograr un fondo blanco de calidad profesional, cumpliendo con los estándares de MercadoLibre.
* FR3.2: El sistema realizará ajustes automáticos básicos a la imagen principal (ej. recorte inteligente, redimensión) para asegurar el cumplimiento de las directrices técnicas de MercadoLibre para la imagen principal del listado.
* FR3.3: En el MVP, las otras imágenes cargadas por el usuario (que no sean la principal) se utilizarán exclusivamente como fuente para la extracción de datos (ver FR2) y no se publicarán como imágenes secundarias en el listado.

**FR4: Generación Inteligente de Contenido de Listado para MercadoLibre (Intelligent Listing Content Generation)**
* FR4.1: El sistema generará automáticamente un título de producto optimizado específicamente para el algoritmo de MercadoLibre y la categoría del producto, utilizando los datos extraídos y aplicando las mejores prácticas de la plataforma.
* FR4.2: El sistema seleccionará o propondrá automáticamente la categoría de MercadoLibre más precisa y adecuada para el producto, basándose en los datos extraídos (y la API de ML según Historia 2.3).
* FR4.3: El sistema completará automáticamente la ficha técnica (atributos/características) de MercadoLibre utilizando los datos extraídos y la información de categoría, priorizando los atributos requeridos y los recomendados clave.
* FR4.4: El sistema generará automáticamente una descripción del producto que sea informativa, esté bien estructurada y aplique las mejores prácticas de MercadoLibre, basándose en los datos extraídos.
* FR4.5: El sistema generará contenido para una única publicación estándar de MercadoLibre por producto (el MVP no incluirá soporte para variantes de producto ni para la creación de múltiples tipos de publicación).
* FR4.6: El sistema **no** incluirá ni gestionará información de precio o stock en el contenido del listado que genera; estos se consideran datos gestionados externamente para el MVP.

**FR5: Flujo de Trabajo de Feedback, Revisión y Aprobación y Publicación (Feedback, Review, Approval & Publishing Workflow)**
* FR5.1: El sistema analizará la calidad de las imágenes en bruto proporcionadas, tanto para su idoneidad para la extracción de datos como para el procesamiento de la imagen principal.
* FR5.2: Si los inputs son críticamente insuficientes, el sistema proporcionará feedback específico y accionable con propuestas claras/call to action.
* FR5.3: El sistema presentará al usuario un borrador completo del contenido del listado generado para su revisión. El flujo de trabajo estándar requerirá la **aprobación explícita del usuario.**
* **FR5.3.1 (Opción de Flujo Automatizado):** El sistema deberá ofrecer una **configuración opcional** que permita al usuario activar un flujo más automatizado. En este modo, si el "índice de confianza" (FR5.4) del contenido generado por la IA para un producto alcanza un umbral predefinido y alto, el sistema podría marcar el contenido como "listo para la etapa de publicación externa" **sin requerir la aprobación explícita individual.**
* FR5.4: El sistema podrá mostrar un "índice de confianza" o un resumen que indique qué tan bien considera que ha podido aplicar las mejores prácticas.
* **FR5.5: Publicación Automatizada del Contenido en MercadoLibre:** Tras la aprobación (explícita o automática), el sistema **intentará publicar automáticamente dicho contenido en MercadoLibre utilizando las APIs correspondientes**, informando al usuario sobre el éxito o fracaso.

**FR6: Interfaz de Usuario / Panel de Control (User Interface / Control Panel)**
* FR6.1: El sistema ofrecerá un panel de control basado en web que sea **100% simple, intuitivo y con un diseño profesional.**
* FR6.2: Permitirá la entrada de datos (prompt mínimo, carga de imágenes) asociadas a un producto.
* FR6.3: Mostrará un listado de productos con su **estado actual claramente identificable, incluyendo indicadores visuales destacados (ej. colores, íconos) basados en el 'índice de confianza' (FR5.4) o si el producto requiere atención específica del usuario.**
* FR6.4: Permitirá **búsquedas básicas y aplicar filtros** a la lista de productos.
* FR6.5: Permitirá editar el prompt inicial o gestionar imágenes *antes* del ciclo de procesamiento.
* FR6.6: Facilitará la revisión y aprobación (o seguimiento en modo automatizado) del contenido generado.
* FR6.7: Mostrará claramente cualquier feedback del sistema o mensajes de error.

## 3. Non-Functional Requirements (MVP)

* **NFR1: Usabilidad (Usability)**
    * NFR1.1: La interfaz de usuario del Panel de Control debe ser percibida por los usuarios objetivo como **100% intuitiva, moderna y profesional.**
    * NFR1.2: Un usuario nuevo deberá ser capaz de completar el flujo de generación de contenido para su primer producto en **menos de [X] minutos de tiempo de interacción activa** (excluyendo tiempos de espera por IA). *(X a definir, objetivo: muy rápido).*
    * NFR1.3: La interfaz del Panel de Control debe ser **altamente responsiva.**
* **NFR2: Rendimiento del Sistema (System Performance)**
    * NFR2.1: El sistema debe **mantener al usuario claramente informado sobre el progreso** de las tareas de IA de fondo.
    * NFR2.2: Los tiempos de procesamiento de IA, aunque variables, no deben ser percibidos como "irrazonables" para un MVP.
* **NFR3: Fiabilidad y Disponibilidad (Reliability & Availability)**
    * NFR3.1: Funcionalidades centrales deben operar consistentemente con inputs adecuados.
    * NFR3.2: Gestión de errores controlada con mensajes útiles.
    * **NFR3.3: Disponibilidad (Uptime): Para el MVP, aspirar a un 99%.** (Dado el uso periódico esperado).
* **NFR4: Seguridad (Security)**
    * NFR4.1: Comunicaciones sobre **HTTPS.**
    * NFR4.2: Manejo seguro de claves de API de MercadoLibre (almacenamiento encriptado, acceso restringido).
* **NFR5: Mantenibilidad y Extensibilidad (Maintainability & Extensibility)**
    * NFR5.1: Arquitectura **inherentemente modular** (Hexagonal, static duck typing).
    * NFR5.2: Código y documentación bajo principios **"agent coding first".**
    * NFR5.3: Diseño MVP no debe impedir estructuralmente futura extensibilidad a otras plataformas.
* **NFR6: Integridad de Datos (Data Integrity)**
    * NFR6.1: Asegurar que los datos del producto se mantengan precisos, consistentes y sin corrupción.
* **NFR7: Persistencia de Datos (Data Persistence)**
    * NFR7.1: Persistir de forma segura datos de trabajo del usuario (prompts, refs. imágenes, contenido IA, estados).
    * NFR7.2: Prevenir pérdida de trabajo entre sesiones o interrupciones.
    * NFR7.3: Modelo de persistencia interna no necesita ser estrictamente transaccional ACID para cada operación en MVP.
* **NFR8: Puerta de Calidad para Finalización de Historias (Definition of Done):**
    * NFR8.1: Antes de que cualquier historia de desarrollo sea considerada 'completa', deberá pasar exitosamente todos los chequeos de calidad automatizados (linting, formateo, tipos, arquitectura) y todas las pruebas automatizadas relevantes.

## 4. User Interaction and Design Goals

Esta sección describe la visión y los objetivos de alto nivel para la Experiencia de Usuario (UX) y la Interfaz de Usuario (UI) del MVP de "IntelliPost AI". Servirá como un brief fundamental para el trabajo posterior del Design Architect.

1.  **Visión General y Experiencia Deseada:**
    * El sistema encarnará la **Eficiencia Profesional y Minimalista**. El diseño será moderno, limpio, con un enfoque absoluto en la funcionalidad sin elementos superfluos, utilizando una paleta de colores profesional o neutra y una tipografía clara y altamente legible. La experiencia del usuario buscará que este se sienta en control, eficiente, y que perciba la herramienta como un asistente experto, directo y potente: "Poder bajo el capó, simplicidad en la superficie".
    * Incorporar mecanismos de **micro-inducción sutil y consejos contextuales** para ayudar a los usuarios nuevos a descubrir y aprovechar las capacidades de la IA dentro de la UI minimalista.
2.  **Paradigmas Clave de Interacción:**
    * La interacción se centrará en un **Panel de Control Central con Acciones Detalladas por Producto**. Los usuarios gestionarán una lista de sus productos en una vista principal tipo dashboard. Al seleccionar un producto específico, accederán a las acciones y a las vistas detalladas correspondientes a ese ítem.
3.  **Pantallas/Vistas Centrales (Conceptuales para el MVP):**
    * Un **Panel de Control Principal** (lista de productos y estados, con "Secciones Inteligentes" o vistas predefinidas por prioridad para facilitar el escaneo rápido).
    * Al seleccionar un producto, una **Vista Única Consolidada para el "Producto en Proceso"** (con información organizada en secciones colapsables y "divulgación progresiva" para manejar la densidad de información, y una guía visual o "checklist de revisión" para ítems retomados de móvil).
4.  **Aspiraciones de Accesibilidad (MVP):**
    * El MVP se enfocará en los **Fundamentos de Accesibilidad**: Navegación Completa por Teclado para funciones esenciales, Contraste de Color Adecuado para la legibilidad (ej. ratios WCAG AA), y Textos Alternativos Claros para iconos y controles no textuales.
5.  **Consideraciones de Branding (Alto Nivel para el MVP):**
    * El MVP establecerá la **identidad visual propia y distintiva de "IntelliPost AI"**. No incorporará personalización de marca para el usuario en esta versión.
6.  **Dispositivos/Plataformas Objetivo (UI Web para el MVP):**
    * **Carga de Inputs Iniciales (Prompt e Imágenes):** Optimizada para **dispositivos móviles.**
    * **Funcionalidad Completa del Panel de Control (Revisión, Edición, Gestión de Estados):** Optimizada para **entornos de escritorio y tablet**, con accesibilidad responsive básica en móviles.
7.  **Principio de Diseño Adicional (Visión de Futuro):**
    * Aunque el MVP se enfoca en productos individuales, el diseño del Panel de Control y la presentación de la información deben **concebirse considerando la futura incorporación de funcionalidades de gestión de lotes y variantes**, favoreciendo estructuras de UI adaptables.

## 5. Technical Assumptions (Versión Final Actualizada)

Esta sección describe las decisiones técnicas de alto nivel, los supuestos fundamentales, las preferencias arquitectónicas y los riesgos iniciales identificados que guiarán el diseño y desarrollo del MVP de "IntelliPost AI".

**5.1. Decisiones Arquitectónicas Fundamentales:**
* **5.1.1. Estructura del Repositorio de Código:** **Monorepo**.
    * *Razón:* Simplificar gestión de dependencias, facilitar commits atómicos, consistencia en herramientas, beneficioso para "Agent Coding First".
* **5.1.2. Arquitectura de Servicios de Alto Nivel:** **Monolito Modular (diseñado con Principios Hexagonales).**
    * *Razón:* Alineado con preferencia por componentes modulares y desacoplados. Simplicidad inicial para MVP, facilita evolución futura. La arquitectura Hexagonal, implementada con 'puertos' y 'adaptadores' (o 'resources') por convención estructural validada estáticamente, mitigará riesgos de dependencia de componentes de IA específicos al facilitar su reemplazo.

**5.2. Preferencias y Direcciones para el Stack Tecnológico (MVP):**
* **5.2.1. Lenguaje y Framework para el Backend:** **Python** con **FastAPI**.
    * *Razón:* Ecosistema IA/ML, rendimiento de FastAPI, type hints. Python es un lenguaje en el que los LLMs suelen estar muy bien entrenados, favoreciendo "Agent Coding First".
* **5.2.2. Tecnología para el Panel de Control Frontend:** **Svelte** (con SvelteKit).
    * *Razón:* Preferencia del usuario. Valorado por rendimiento, DX, y capacidad para UIs profesionales.
* **5.2.3. Enfoque para Tecnologías de IA (Dirección Preferente para Investigación y Desarrollo Inicial):** Enfoque híbrido. La investigación (ya provista en `reports/`) y el desarrollo inicial priorizarán y evaluarán:
    * APIs de terceros especializadas para procesamiento visual crítico (ej. fondo blanco).
    * Uso directo de LLMs multimodales para extracción de datos de imágenes.
    * LLMs (multimodales o de texto) para generación de contenido optimizado para MercadoLibre.
    * Alternativas/complementos: librerías Python OCR/NLP, servicios IA de proveedores cloud.
* **5.2.4. Base de Datos:** **PostgreSQL** y **Almacenamiento de Objetos**.
    * *Razón:* PostgreSQL para datos estructurados/semi-estructurados (JSONB). Almacenamiento de Objetos para imágenes.

**5.3. Principios Generales de Desarrollo y Arquitectura (Refinado):**
* **5.3.1. Modularidad Fundamental y Diseño Hexagonal:** Referencia fuerte a Arquitectura Hexagonal (Puertos y Adaptadores) por módulo de funcionalidad, como ilustra el ejemplo del usuario (a compartir con Arquitecto). Se favorecerá que 'adapters' internos cumplan 'puertos' (`typing.Protocol`) por convención estructural validada (ej. Pyright).
* **5.3.2. Comunicación Inter-Módulo Desacoplada:** Patrón con puertos definidos por consumidor y DTOs compartidos (Shared Kernel mínimo y necesario de DDD). Módulos de plataforma (ej. `mercadolibre_manager`) usarán servicios especializados (ej. `image_engine`).
* **5.3.3. "Agent Coding First", Calidad de Código, Tipado Estático Riguroso y Mantenimiento de Fronteras Arquitectónicas:** Optimizar colaboración con LLMs y asegurar alta calidad. Esto incluye:
    * *Linting y Formateo Consistente:* **Ruff** (Python), **ESLint/Prettier** (Svelte/JS/TS).
    * *Tipado Estático Riguroso:* **Pyright** (Python, usando `typing.List` etc.), **TypeScript** (Svelte).
    * *Mantenimiento de Fronteras Arquitectónicas:* **Tach** (Python), **dependency-cruiser** (Svelte/JS/TS).
    * *Documentación del Código (Justa y Necesaria):* Priorizar código auto-documentado. Comentarios/documentación explícita solo cuando sea necesario.
* **5.3.4. Gestión de Costos:** Apertura a servicios de pago razonables.
* **5.3.5. Metodología de Desarrollo Dirigida por Pruebas (TDD): Se adoptará de forma obligatoria la metodología de Desarrollo Dirigido por Pruebas (TDD).** Las pruebas (unitarias y de integración relevantes) se escribirán *antes* del código de la funcionalidad para guiar la implementación y asegurar la corrección, la cobertura y un diseño inherentemente testeable desde el inicio.

**5.4. Supuestos Técnicos y Operacionales Clave:**
* Usuarios pueden capturar imágenes básicas con celulares.
* APIs de MercadoLibre son capaces y fiables para el MVP.
* Existen y son accesibles tecnologías de IA viables.

**5.5. Riesgos Técnicos Identificados (Lista Inicial):**
* Complejidad de Integración (API ML, IA de terceros).
* Rendimiento y Calidad de la IA (especialmente imágenes y extracción de datos).
    * *Mitigación Arquitectónica:* La arquitectura Hexagonal con "adaptadores/resources" intercambiables facilitará el reemplazo o actualización de servicios de IA.

## 6. Epic Overview

*(Esta sección contendrá la lista de los 5 Epics y, debajo de cada uno, los títulos de sus Historias de Usuario, sus Descripciones de Historia y sus Criterios de Aceptación, tal como los hemos definido interactivamente y completado en modo YOLO. Por brevedad en esta respuesta, no repetiré aquí el detalle completo de las ~20 historias que definimos, pero el PRD final las contendrá estructuradas bajo cada Epic correspondiente).*

**Epic 1: Plataforma Base y Panel de Control Inicial (El Cimiento Inteligente)**
* Historia 1.1: Configuración Inicial del Proyecto, Monorepo y Herramientas Centralizadas de Desarrollo y Calidad (con UV para Python).
* Historia 1.2: Armazón Básico de la Aplicación Backend (FastAPI).
* Historia 1.3: Armazón Básico de la Aplicación Frontend (Svelte).
* Historia 1.4: Definición y Configuración Inicial de la Base de Datos (PostgreSQL) incluyendo Modelo de Usuario Básico.
* Historia 1.5: Implementación de Autenticación de Usuario Básica en el Backend.
* Historia 1.6: Implementación del Marco del Panel de Control Básico con Flujo de Login.
* Historia 1.7: Establecimiento del Pipeline Inicial de Integración Continua y Despliegue Continuo (CI/CD).

**Epic 2: Ingesta y Extracción Inteligente de Datos del Producto (La Semilla de Contenido)**
* Historia 2.1: Interfaz para Carga de Inputs Iniciales del Producto (Prompt e Imágenes).
* Historia 2.2: Almacenamiento Seguro de los Inputs Crudos del Producto.
* Historia 2.3: Implementación del Servicio Núcleo de IA para Extracción de Datos (Guiado por MercadoLibre) desde Imágenes y Prompt.
* Historia 2.4: Persistencia de los Datos Estructurados Extraídos por la IA.
* Historia 2.5: Visualización Inicial de Datos Clave Extraídos por la IA en el Panel de Control.

**Epic 3: Automatización Profesional de la Imagen Principal del Producto (La Imagen Estrella)**
* Historia 3.1: Implementación del Motor de Procesamiento de Imagen Principal (`image_engine` - Fondo Blanco, Ajustes y Derivados Básicos).
* Historia 3.2: Persistencia de la Imagen Principal Procesada y sus Metadatos.
* Historia 3.3: Visualización y Validación de la Imagen Principal Procesada y sus Derivados en el Panel de Control.

**Epic 4: AI-Powered Listing Content Generation (El Contenido que Vende)**
* Historia 4.1: Servicio de IA para Generación de Título Optimizado para MercadoLibre.
* Historia 4.2: Servicio de IA para Confirmación/Selección Final de Categoría de MercadoLibre.
* Historia 4.3: Servicio de IA para Completado Estratégico de la Ficha Técnica (Atributos).
* Historia 4.4: Servicio de IA para Generación de Descripción de Producto Estructurada e Informativa.
* Historia 4.5: Consolidación y Persistencia del Contenido de Listado Generado por IA.

**Epic 5: Revisión, Feedback & MercadoLibre Publishing (El Lanzamiento Triunfal)**
* Historia 5.1: UI para Revisión y Edición del Contenido de Listado Completo.
* Historia 5.2: Presentación del Índice de Confianza General y Configuración del Flujo Automatizado Opcional.
* Historia 5.3: Aprobación Final del Usuario y Disparo de Publicación.
* Historia 5.4: Servicio Backend para Publicación en MercadoLibre API (equivale a FR5.5).
* Historia 5.5: Actualización de Estado y Feedback Post-Publicación en Panel de Control.

## 7. Key Reference Documents
1.  **IntelliPost AI - Project Brief (v1.0, English Version)** - *Como se generó con Analyst Mary.*
2.  **User-Provided Architectural Example & Principles (v1.0)** - *Ejemplo detallado de estructura modular Hexagonal provisto por el usuario.*
3.  **Research Report: AI Technology Evaluation for Image Processing & Data Operations** - *Referencia a los archivos en `reports/image_processing/` (claude.md, gemini.md, x.md).*
4.  **Research Report: MercadoLibre Publishing Best Practices & Algorithm Insights** - *Referencia a los archivos en `reports/publishing/meli/` (claude.md, gemini.md, x.md).*
5.  **Research Report: Universal Principles of Persuasive & High-Conversion Publishing** - *Referencia a los archivos en `reports/publishing/general/` (claude.md, gemini.md, x.md).*
6.  **Research Prompts (Generated)** - *Los 3 prompts detallados generados durante la fase de PRD como mandato para las investigaciones, cuyos hallazgos iniciales están en los reportes anteriores.*

## 8. Out of Scope Ideas Post MVP
Las siguientes funcionalidades se consideran explícitamente fuera del alcance del MVP y se evaluarán para futuras versiones:
* Gestión de Variantes de Producto.
* Soporte para Múltiples Tipos de Publicación por Producto en MercadoLibre.
* Carga y Procesamiento por Lotes (Batch).
* Generación Avanzada y Variada de Imágenes Secundarias (ej. estilo de vida).
* Adaptación Automática del Sistema a Cambios en las Reglas de las Plataformas.
* Extensibilidad del Publicador a Otras Plataformas de E-commerce.
* Módulo de Analíticas de Rendimiento y Sugerencias de Optimización (Post-Publicación).
* Funcionalidades Avanzadas de Asistencia para Palabras Clave y Tendencias (más allá del MVP).
* Funcionalidad de "Olvidé mi Contraseña" Automatizada.
* Auto-Registro de Usuarios / Gestión Multi-Cliente Completa.
* Funcionalidad de "Guardar Borrador" para Inputs Iniciales.
* Accesibilidad Detallada (Más allá de los Fundamentos del MVP).

## 9. Change Log
| Change | Date | Version | Description | Author |
| ------ | ---- | ------- | ----------- | ------ |
| Creación Inicial | 2025-05-27 | 1.0 | Creación inicial del PRD. | John (PM) |

--- END PRD START CHECKLIST OUTPUT ------

## 10. Checklist Results Report
*(Esta sección será completada por el PM John después de revisar el PRD con el `pm-checklist`)*

--- END Checklist START Design Architect `UI/UX Specification Mode` Prompt ------

## 11. Prompt for Design Architect (UI/UX Specification Mode)

**Objective:** Elaborate on the UI/UX aspects of the product defined in this PRD.
**Mode:** UI/UX Specification Mode
**Input:** This completed PRD document.
**Key Tasks:**
1. Review the product goals, user stories, and UI-related notes and "User Interaction and Design Goals" herein.
2. Collaboratively define detailed user flows, wireframes (conceptual), and key screen mockups/descriptions for the Svelte-based Panel de Control.
3. Specify usability requirements and ensure adherence to the "Fundamentos de Accesibilidad" defined.
4. Populate or create the `front-end-spec-tmpl` document (o un documento equivalente de Especificación UI/UX).
5. Ensure that this PRD is updated or clearly references the detailed UI/UX specifications derived from your work, so that it provides a comprehensive foundation for subsequent architecture and development phases.
   Please guide the user through this process to enrich the PRD with detailed UI/UX specifications.

--- END Design Architect `UI/UX Specification Mode` Prompt START Architect Prompt ------

## 12. Initial Architect Prompt

Based on our discussions and requirements analysis for the "IntelliPost AI" project, I've compiled the following technical guidance from this PRD to inform your architecture analysis and decisions, to kick off the Architecture Creation Mode:

### Technical Infrastructure and Decisions (from PRD Section 5: Technical Assumptions)

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
