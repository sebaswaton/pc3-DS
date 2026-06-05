# Requisitos Funcionales — Voz del Ciudadano

**Versión:** 1.0 | **Fecha:** 2026-06-05

---

## Actores

| ID | Actor | Rol |
|----|-------|-----|
| A01 | Ciudadano registrado | Firma iniciativas, comenta y sube recursos |
| A02 | Colectivo civil | Crea y gestiona iniciativas legislativas |
| A03 | Administrador | Modera contenido y configura el sistema |
| A04 | Oficina del Congreso | Recibe el expediente sellado |
| A05 | RENIEC (sistema externo) | Valida identidad del ciudadano |

---

## RF-01 — Registro y Verificación de Identidad

**Prioridad:** Alta | **Patrón:** Adapter (`ReniecAdapter`)

El sistema permite el registro de ciudadanos y colectivos mediante correo + contraseña. Para poder firmar una iniciativa, el ciudadano debe verificar su identidad a través del adaptador RENIEC. El sistema almacena únicamente el estado de verificación, nunca datos biométricos.

**Criterio de aceptación:**
- Un ciudadano no verificado no puede firmar.
- El adaptador responde en < 3 s o emite timeout con mensaje de error.
- Las contraseñas se almacenan con bcrypt (factor ≥ 12).

---

## RF-02 — Creación y Publicación de Iniciativa

**Prioridad:** Alta | **Patrón:** Facade (`InitiativeFacade`)

Un colectivo civil autenticado puede crear una iniciativa con: título (máx. 200 chars), exposición de motivos, articulado normativo y documentos PDF adjuntos (máx. 50 MB). Al publicarla, el estado cambia de `BORRADOR` a `ACTIVA`, se inicia el contador de 90 días y el de firmas en 0.

**Criterio de aceptación:**
- Se genera un ID único de expediente al crear.
- La fecha UTC de publicación es inmutable una vez registrada.
- La operación completa se expone al cliente a través de `InitiativeFacade`.

---

## RF-03 — Firma Digital de Iniciativa

**Prioridad:** Alta | **Patrón:** Decorator (`ValidatedSignatureDecorator`)

Un ciudadano verificado puede firmar una iniciativa `ACTIVA`. El sistema registra: hash anonimizado del firmante, timestamp UTC, hash SHA-256 del documento en ese instante e IP enmascarada. El `ValidatedSignatureDecorator` añade la validación anti-duplicado y el enriquecimiento de metadata sin modificar la clase base de firma.

**Criterio de aceptación:**
- Un ciudadano no puede firmar la misma iniciativa dos veces.
- La firma queda en estado `VÁLIDA` o `RECHAZADA` según las validaciones.

---

## RF-04 — Contenido de Apoyo (comentarios, modificaciones y recursos)

**Prioridad:** Media | **Patrón:** Composite (`CommentNode`)

Los ciudadanos registrados pueden agregar comentarios (máx. 2 000 chars) con respuestas anidadas (máx. 3 niveles). Los ciudadanos verificados pueden proponer modificaciones al articulado y subir recursos (PDF/DOCX ≤ 10 MB, imágenes ≤ 5 MB, URL de video). Los archivos son escaneados con antivirus antes de almacenarse. La estructura de comentarios se modela como árbol Composite.

**Criterio de aceptación:**
- Los formatos no permitidos son rechazados con mensaje descriptivo.
- Si el colectivo acepta una modificación, el articulado se versiona y se notifica a los firmantes previos.

---

## RF-05 — Sellado Criptográfico y Envío al Congreso

**Prioridad:** Alta | **Patrón:** Proxy (`CryptographicSealProxy`)

Al acumularse 25 000 firmas válidas (o al expirar los 90 días), el `CryptographicSealProxy` evalúa la transición de estado. Si se alcanza el umbral, genera hash SHA-512 del expediente completo, lo firma con la clave privada del sistema (RSA-4096), lo congela como solo lectura y lo envía a la Oficina del Congreso vía API segura (TLS 1.3). Si el envío falla, reintenta 3 veces con backoff exponencial.

**Criterio de aceptación:**
- Cualquier escritura posterior al sellado es rechazada por el Proxy.
- El estado pasa a `ENVIADA` únicamente tras acuse de recibo exitoso.
- Los umbrales (25 000 firmas / 90 días) son configurables sin redespliegue.

---

## Matriz de patrones × requisitos

| Requisito | Facade | Adapter | Decorator | Proxy | Composite |
|-----------|:------:|:-------:|:---------:|:-----:|:---------:|
| RF-01     |        | ✓       |           |       |           |
| RF-02     | ✓      |         |           |       |           |
| RF-03     |        |         | ✓         |       |           |
| RF-04     |        |         |           |       | ✓         |
| RF-05     | ✓      |         |           | ✓     |           |
