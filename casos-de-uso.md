# Casos de Uso — Voz del Ciudadano

**Versión:** 1.0 | **Fecha:** 2026-06-05

---

## Diagrama de actores (textual)

```
[Ciudadano registrado] ──► CU-01, CU-03, CU-04
[Colectivo civil]      ──► CU-02, CU-04
[Sistema (scheduler)]  ──► CU-05
[Oficina del Congreso] ──► CU-05 (receptor)
[RENIEC]               ──► CU-01 (sistema externo)
```

---

## CU-01 — Verificar Identidad Ciudadana

| Campo | Detalle |
|-------|---------|
| **Actor principal** | Ciudadano registrado |
| **Actor secundario** | RENIEC (vía `ReniecAdapter`) |
| **Precondición** | Usuario autenticado con cuenta registrada |
| **Postcondición** | Estado de verificación actualizado a `VERIFICADO` |
| **Patrón** | Adapter |

**Flujo principal:**
1. El ciudadano accede a "Verificar mi identidad".
2. El sistema invoca `ReniecAdapter.verify(dni, datosPersonales)`.
3. El adaptador traduce la llamada al formato del servicio RENIEC.
4. RENIEC responde con resultado de validación.
5. El sistema actualiza el perfil a `VERIFICADO` y notifica al usuario.

**Flujo alternativo — timeout RENIEC:**
- En el paso 4, si no hay respuesta en 3 s, el Adapter lanza `VerificationTimeoutException` y se muestra mensaje de reintento.

---

## CU-02 — Crear y Publicar Iniciativa Legislativa

| Campo | Detalle |
|-------|---------|
| **Actor principal** | Colectivo civil |
| **Precondición** | Colectivo autenticado y verificado |
| **Postcondición** | Iniciativa en estado `ACTIVA` con contador de 90 días iniciado |
| **Patrón** | Facade (`InitiativeFacade`) |

**Flujo principal:**
1. El colectivo completa el formulario (título, articulado, documentos).
2. El sistema crea la iniciativa en estado `BORRADOR` y genera un ID único.
3. El colectivo selecciona "Publicar".
4. `InitiativeFacade.publish(iniciativaId)` orquesta: validación de contenido, inicio del temporizador y cambio de estado a `ACTIVA`.
5. El sistema notifica al colectivo y publica en el portal.

**Flujo alternativo — contenido inválido:**
- En el paso 4, si el articulado supera el límite o el PDF excede 50 MB, la Facade retorna error de validación y el estado permanece en `BORRADOR`.

---

## CU-03 — Firmar una Iniciativa

| Campo | Detalle |
|-------|---------|
| **Actor principal** | Ciudadano verificado |
| **Precondición** | Iniciativa en estado `ACTIVA`; ciudadano con estado `VERIFICADO` |
| **Postcondición** | Firma registrada como `VÁLIDA`; contador incrementado en 1 |
| **Patrón** | Decorator (`ValidatedSignatureDecorator`) |

**Flujo principal:**
1. El ciudadano pulsa "Firmar" en una iniciativa activa.
2. `ValidatedSignatureDecorator.sign(ciudadanoId, iniciativaId)` ejecuta:
   - Validación anti-duplicado.
   - Enriquecimiento con hash SHA-256 del documento actual y timestamp UTC.
3. La firma base es persistida con estado `VÁLIDA`.
4. El contador de firmas se incrementa atómicamente.
5. Se muestra confirmación al ciudadano.

**Flujo alternativo — firma duplicada:**
- En el paso 2, el Decorator detecta firma previa y lanza `DuplicateSignatureException` sin persistir.

---

## CU-04 — Agregar Contenido de Apoyo

| Campo | Detalle |
|-------|---------|
| **Actor principal** | Ciudadano registrado / Colectivo civil |
| **Precondición** | Iniciativa en estado `ACTIVA` |
| **Postcondición** | Comentario, modificación o recurso vinculado a la iniciativa |
| **Patrón** | Composite (`CommentNode`) |

**Flujo principal:**
1. El usuario elige el tipo de aporte: comentario, modificación o recurso.
2. **Comentario:** se crea un `CommentNode` y se inserta como hijo del nodo seleccionado (raíz o respuesta, máx. 3 niveles).
3. **Modificación:** se registra la propuesta de cambio al articulado; el colectivo recibe notificación para aprobar/rechazar.
4. **Recurso:** el archivo pasa por escaneo antivirus; si es aprobado, se almacena vinculado a la iniciativa.
5. El contenido aparece en el panel público en < 2 s.

**Flujo alternativo — formato de archivo no permitido:**
- En el paso 4, el sistema rechaza el archivo y muestra mensaje con formatos admitidos.

---

## CU-05 — Sellado Criptográfico y Envío al Congreso

| Campo | Detalle |
|-------|---------|
| **Actor principal** | Sistema (scheduler automático) |
| **Actor secundario** | Oficina del Congreso |
| **Precondición** | Iniciativa `ACTIVA` alcanza 25 000 firmas válidas O expiran 90 días |
| **Postcondición** | Expediente sellado y en estado `ENVIADA` (o `EXPIRADA`) |
| **Patrón** | Proxy (`CryptographicSealProxy`), Facade (`InitiativeFacade`) |

**Flujo principal — umbral alcanzado:**
1. El scheduler detecta que el contador llega a 25 000.
2. `CryptographicSealProxy.seal(iniciativaId)`:
   - Congela el expediente (solo lectura).
   - Genera hash SHA-512 del contenido completo.
   - Firma el hash con clave privada RSA-4096.
   - Registra sello en log de auditoría inmutable.
3. `InitiativeFacade.sendToCongress(iniciativaId)` envía el expediente vía API TLS 1.3.
4. La Oficina confirma recepción con número de radicación.
5. El estado cambia a `ENVIADA`; los firmantes son notificados.

**Flujo alternativo — fallo de envío:**
- En el paso 3, si la API falla, el sistema reintenta 3 veces (backoff exponencial). Si persiste, notifica al administrador y mantiene estado `LISTA_PARA_ENVÍO`.

**Flujo alternativo — expiración sin umbral:**
- Si expiran 90 días sin 25 000 firmas, el Proxy cambia el estado a `EXPIRADA` sin sellar ni enviar.
