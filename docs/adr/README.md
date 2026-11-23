# Registro de decisiones arquitectónicas — VELMORA

Cada ADR documenta una decisión importante, su contexto, alternativas y consecuencias. Los ADR son versionados con Git; si una decisión cambia, crear un nuevo ADR que la sustituya y conservar el histórico.

| ADR | Estado | Decisión |
| --- | --- | --- |
| [ADR-001](0001-monorepo.md) | Propuesto | Un monorepo con API, web, Supabase y documentación |
| [ADR-002](0002-vercel-fastapi.md) | Propuesto | Vercel para React/Vite y FastAPI, en dos proyectos |
| [ADR-003](0003-rls-jwt-supabase.md) | Propuesto | JWT verificado, RLS y clientes separados por privilegios |
| [ADR-004](0004-patrones-diseno.md) | Propuesto | Seis patrones GoF y patrones arquitectónicos adicionales |

## Alcance inicial

VELMORA es una plataforma educativa para explorar inversiones según presupuesto, riesgo y categorías, no para gestionar inversiones o dinero reales. El módulo de **lecciones/progreso** amplía el documento inicial de la idea y se incluye porque se ha propuesto explícitamente en el plan técnico. Los datos de inversión serán inicialmente ilustrativos, con advertencias de riesgo y sin promesas de rendimiento.

## Convenciones

- Fecha de propuesta: 2026-11-22.
- Estados: Propuesto, Aceptado, Sustituido.
- Formato: Contexto → Decisión → Alternativas → Consecuencias → Verificación.
