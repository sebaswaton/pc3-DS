# Casos de Prueba — Voz del Ciudadano

**Versión:** 1.0 | **Fecha:** 2026-06-05

---

## CP-01 — Verificación de Identidad vía ReniecAdapter

**RF asociado:** RF-01 | **CU asociado:** CU-01 | **Patrón:** Adapter

| Campo | Detalle |
|-------|---------|
| **Objetivo** | Verificar que `ReniecAdapter` traduce correctamente la petición y procesa la respuesta de RENIEC |
| **Precondición** | Usuario autenticado, estado `NO_VERIFICADO`; mock del servicio RENIEC disponible |

| # | Escenario | Entrada | Resultado esperado |
|---|-----------|---------|-------------------|
| 1 | Verificación exitosa | DNI válido + datos correctos | Estado cambia a `VERIFICADO`; sin datos biométricos almacenados |
| 2 | Datos incorrectos | DNI válido + nombre incorrecto | Estado permanece `NO_VERIFICADO`; mensaje de error descriptivo |
| 3 | Timeout RENIEC | Servicio no responde en 3 s | `VerificationTimeoutException`; mensaje de reintento mostrado al usuario |
| 4 | Ciudadano ya verificado | Intento de segunda verificación | Sistema retorna estado actual sin volver a llamar a RENIEC |

---

## CP-02 — Creación y Publicación de Iniciativa (InitiativeFacade)

**RF asociado:** RF-02 | **CU asociado:** CU-02 | **Patrón:** Facade

| Campo | Detalle |
|-------|---------|
| **Objetivo** | Confirmar que `InitiativeFacade.publish()` orquesta correctamente validación, temporizador y cambio de estado |
| **Precondición** | Colectivo autenticado y verificado; iniciativa en estado `BORRADOR` |

| # | Escenario | Entrada | Resultado esperado |
|---|-----------|---------|-------------------|
| 1 | Publicación exitosa | Iniciativa con todos los campos válidos | Estado → `ACTIVA`; contador de 90 días iniciado; ID único generado |
| 2 | PDF excede límite | Archivo adjunto de 55 MB | Facade retorna `ValidationException`; estado permanece `BORRADOR` |
| 3 | Título vacío | Título = `""` | Error de validación antes de llamar a subsistemas internos |
| 4 | Publicación doble | Llamar publish() sobre iniciativa ya `ACTIVA` | `IllegalStateException`; estado no cambia |

---

## CP-03 — Firma con Validación Anti-duplicado (ValidatedSignatureDecorator)

**RF asociado:** RF-03 | **CU asociado:** CU-03 | **Patrón:** Decorator

| Campo | Detalle |
|-------|---------|
| **Objetivo** | Verificar que el Decorator añade correctamente validación anti-duplicado y enriquecimiento de metadata |
| **Precondición** | Iniciativa `ACTIVA`; ciudadano con estado `VERIFICADO` |

| # | Escenario | Entrada | Resultado esperado |
|---|-----------|---------|-------------------|
| 1 | Primera firma válida | Ciudadano verificado + iniciativa activa | Firma persiste en estado `VÁLIDA`; contador incrementado en 1 |
| 2 | Firma duplicada | Mismo ciudadano + misma iniciativa | `DuplicateSignatureException`; contador no cambia |
| 3 | Ciudadano no verificado | Estado `NO_VERIFICADO` | Acceso denegado antes de llegar al Decorator |
| 4 | Firma sobre iniciativa expirada | Iniciativa en `EXPIRADA` | `InvalidInitiativeStateException`; firma rechazada |

---

## CP-04 — Árbol de Comentarios (CommentNode Composite)

**RF asociado:** RF-04 | **CU asociado:** CU-04 | **Patrón:** Composite

| Campo | Detalle |
|-------|---------|
| **Objetivo** | Validar la estructura jerárquica de comentarios y el límite de profundidad de 3 niveles |
| **Precondición** | Iniciativa `ACTIVA`; usuario autenticado |

| # | Escenario | Entrada | Resultado esperado |
|---|-----------|---------|-------------------|
| 1 | Comentario raíz | Texto válido sin padre | `CommentNode` creado como hijo directo de la iniciativa |
| 2 | Respuesta de nivel 2 | Comentario hijo de un comentario raíz | Nodo insertado correctamente en nivel 2 del árbol |
| 3 | Intento de nivel 4 | Respuesta a comentario de nivel 3 | `MaxDepthExceededException`; comentario rechazado |
| 4 | Comentario vacío | Texto = `""` | `ValidationException` antes de crear el nodo |

---

## CP-05 — Sellado Criptográfico y Envío (CryptographicSealProxy)

**RF asociado:** RF-05 | **CU asociado:** CU-05 | **Patrón:** Proxy, Facade

| Campo | Detalle |
|-------|---------|
| **Objetivo** | Verificar que el Proxy sella correctamente el expediente, deniega escrituras posteriores y gestiona el envío al Congreso |
| **Precondición** | Iniciativa `ACTIVA` con 25 000 firmas válidas registradas |

| # | Escenario | Entrada | Resultado esperado |
|---|-----------|---------|-------------------|
| 1 | Sellado exitoso | Iniciativa alcanza 25 000 firmas | Hash SHA-512 generado; expediente en solo lectura; log de auditoría actualizado |
| 2 | Escritura post-sellado | Intento de agregar firma tras sello | Proxy lanza `SealedExpedientException`; operación rechazada |
| 3 | Envío exitoso al Congreso | API del Congreso responde OK | Estado → `ENVIADA`; número de radicación registrado; firmantes notificados |
| 4 | Fallo de envío con reintentos | API falla 3 veces consecutivas | Sistema notifica al administrador; estado permanece `LISTA_PARA_ENVÍO` |
| 5 | Expiración sin umbral | 90 días transcurridos con < 25 000 firmas | Estado → `EXPIRADA`; no se sella ni se envía |
