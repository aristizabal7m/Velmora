# ADR-002: Desplegar React y FastAPI en Vercel

- **Fecha:** 2026-11-22
- **Estado:** Propuesto
- **Decisores:** Equipo de VELMORA

## Contexto

Se desea una demo universitaria accesible por Internet, integrada con GitHub y que publique cambios a través de PRs. El frontend será React + TypeScript + Vite; el backend, FastAPI con Python 3.12. La API prestará operaciones HTTP de corta duración.

## Decisión

Crear dos proyectos independientes en Vercel que usen el mismo repositorio:

- `velmora-web` con Root Directory `apps/web` y compilación de Vite.
- `velmora-api` con Root Directory `apps/api`, desplegando la aplicación FastAPI en Vercel Functions.
- Usar un punto de entrada explícito en `apps/api/pyproject.toml`, por ejemplo:

```toml
[tool.vercel]
entrypoint = "velmora.main:app"
```

El paquete `velmora` debe estar instalable/descubrible desde `src` en el entorno de despliegue; en Fase 9 se probará la configuración real y, si hace falta, se ajustará el empaquetado o se incluirá un adaptador `app.py` en la raíz del proyecto API.

- `main` desplegará a producción; ramas/PRs crearán previsualizaciones. Las previsualizaciones deberán usar API y datos de **staging**, no una base de datos productiva con datos reales.
- Definir CORS únicamente para orígenes conocidos y autorizados; nunca asumir que CORS sustituye autenticación o autorización.
- Los endpoints y funcionalidades estarán diseñados para no requerir procesos permanentes en memoria.

## Alternativas consideradas

1. **Render/Fly.io/Railway para backend:** adecuados para procesos persistentes y trabajos largos, pero requieren otra plataforma.
2. **Todo en un único despliegue:** reduce cantidad de proyectos, pero dificulta separar configuración de frontend y API en este plan.
3. **Servidor Ubuntu propio:** mayor control, pero aumenta mantenimiento y configuración de seguridad.

## Consecuencias

- **Ventajas:** integración GitHub, URLs de previews, infraestructura sencilla para demo, despliegue independiente por aplicación.
- **Costos/riesgos:** límites de funciones, arranques en frío, configuración de rutas y dependencia de Vercel; conexiones de base de datos requieren cuidado en serverless.
- **Plan de salida:** conservar dominio y servicios FastAPI independientes del runtime para poder mover la API si hace falta.

## Verificación

- `GET /health` responde en producción y staging.
- React consume la API mediante `VITE_API_URL` (variable pública que contiene solo la URL, no claves).
- Los dos proyectos se reconstruyen desde el mismo repositorio y sus respectivos directorios raíz.
- Se comprueba un flujo completo sin depender de memoria persistente en la función.

## Referencias

- https://vercel.com/docs/frameworks/backend/fastapi
- https://vercel.com/docs/monorepos
