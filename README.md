# Voz del Ciudadano — Plataforma de Iniciativas Legislativas

**Institución:** Legislativo de la República  
**Versión:** 1.0 | **Fecha:** 2026-06-05

## Descripción

Portal digital que permite a colectivos civiles crear propuestas normativas, recolectar firmas digitales ciudadanas y, al alcanzar 25 000 firmas válidas en ≤ 90 días, congelar criptográficamente el expediente y enviarlo a la Oficina del Congreso.

## Documentos

| Archivo | Contenido |
|---------|-----------|
| [requisitos-funcionales.md](requisitos-funcionales.md) | 5 Requisitos Funcionales |
| [casos-de-uso.md](casos-de-uso.md) | 5 Casos de Uso |
| [casos-de-prueba.md](casos-de-prueba.md) | 5 Casos de Prueba |

## Patrones Estructurales Aplicados

| # | Patrón | Clase principal | Rol en el sistema |
|---|--------|-----------------|-------------------|
| 1 | **Facade** | `InitiativeFacade` | Interfaz única que orquesta firma, sellado y envío al Congreso |
| 2 | **Adapter** | `ReniecAdapter` | Traduce el servicio externo de identidad RENIEC a la interfaz interna |
| 3 | **Decorator** | `ValidatedSignatureDecorator` | Añade validación anti-duplicado y enriquecimiento de metadata a las firmas |
| 4 | **Proxy** | `CryptographicSealProxy` | Controla el acceso al expediente; deniega escrituras tras el sellado |
| 5 | **Composite** | `CommentNode` | Modela comentarios y respuestas anidadas como árbol parte-todo |

## Estados de una Iniciativa

```
BORRADOR → ACTIVA → LISTA_PARA_ENVÍO → ENVIADA
                 ↘ EXPIRADA (90 días sin 25 000 firmas)
```

## Stack tecnológico previsto

- **Backend:** Java 21 / Spring Boot 3
- **Frontend:** React 18 + TypeScript
- **Base de datos:** PostgreSQL 16
- **Mensajería:** RabbitMQ
- **Gestión de ramas:** Git Flow
