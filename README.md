# VELMORA

**Un universo de inversiones a tu alcance.**

VELMORA es una aplicación web educativa orientada a personas en Colombia que desean conocer y comparar alternativas de inversión. Permite filtrar opciones por riesgo, categoría y monto, consultar lecciones básicas y registrar progreso con autenticación.

## Objetivo

Presentar información clara sobre opciones de inversión, sus requisitos, riesgos y características, sin gestionar dinero real ni prometer rentabilidad.

## Tecnologías

- Backend: Python 3.12 + FastAPI + Pydantic
- Frontend: React + TypeScript + Vite + React Router
- Base de datos: PostgreSQL (Supabase) con RLS y Storage
- Autenticación: Supabase Auth + JWT verificado por JWKS en FastAPI
- Pruebas: pytest, Vitest/Testing Library, pgTAP
- Calidad: Ruff, mypy, oxlint, TypeScript
- Despliegue: Vercel (dos proyectos)

## Estructura

```text
apps/api/     FastAPI, patrones GoF, repositorios, servicios y tests
apps/web/     Cliente React, autenticación, rutas, filtros y tests
supabase/     Migraciones, seed, políticas RLS y pruebas pgTAP
docs/adr/     Decisiones arquitectónicas
docs/uml/     Diagramas Mermaid de los seis patrones
.github/      CI y dependabot
```

## Inicio rápido

Requisitos: Python 3.12, uv, Node 22+, Docker y Supabase CLI.

```bash
git clone https://github.com/aristizabal7m/Velmora.git
cd Velmora

# API
cd apps/api
uv sync
uv run fastapi dev src/velmora/main.py

# Web (en otra terminal)
cd apps/web
npm install
npm run dev

# Base de datos local (en otra terminal, desde la raíz)
npm install
./node_modules/.bin/supabase start
./node_modules/.bin/supabase db reset
```

La API queda en `http://localhost:8000` y la web en `http://localhost:5173`.

### Variables de entorno

Copiar los archivos ejemplo y completarlos sin versionar secretos:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

| Ubicación | Variable | Uso |
| --- | --- | --- |
| API | `ENVIRONMENT` | `local` o `production` |
| API | `SUPABASE_URL` | URL del proyecto Supabase |
| API | `SUPABASE_PUBLISHABLE_KEY` | Clave pública; segura en cliente |
| API | `SUPABASE_SECRET_KEY` | Solo servidor; habilita contexto admin |
| API | `SUPABASE_JWKS_URL` | Opcional; por defecto `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` |
| API | `CORS_ORIGINS` | Orígenes permitidos separados por comas |
| Web | `VITE_API_URL` | URL base de la API |
| Web | `VITE_SUPABASE_URL` | URL de Supabase Auth |
| Web | `VITE_SUPABASE_PUBLISHABLE_KEY` | Clave pública de Supabase |

Nunca definir `VITE_SUPABASE_SECRET_KEY`: Vite incrusta las variables `VITE_*` en el bundle.

## Comandos de verificación

Desde la raíz:

```bash
npm run check
npm test
./node_modules/.bin/supabase test db
```

Por aplicación:

```bash
cd apps/api && uv run pytest -q && uv run ruff check . && uv run mypy src tests
cd apps/web && npm run typecheck && npm run lint && npm test && npm run build
```

Estado actual verificado: 22 tests Python, 3 tests web y 7 pruebas pgTAP en verde; Ruff, mypy, oxlint, TypeScript y build sin errores.

## API

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Estado del servicio y entorno |
| `GET` | `/api/v1/investments` | Inversiones publicadas con filtros `risk`, `category`, `min_amount`, `max_amount` |
| `GET` | `/api/v1/investments/recommendations` | Recomendaciones por `profile` |
| `GET` | `/api/v1/investments/mine` | Contexto del usuario autenticado (401 si no hay JWT) |
| `GET` | `/api/v1/investments/all` | Incluye no publicadas; requiere rol `admin` |
| `GET` | `/api/v1/investments/{slug}` | Detalle de una inversión |
| `GET` | `/api/v1/categories` | Categorías publicadas |
| `GET` | `/api/v1/lessons` | Lecciones publicadas |
| `POST` | `/api/v1/lessons/{id}/complete` | Registra progreso y notifica observadores |
| `GET` | `/api/v1/auth/me` | Usuario actual sin exponer el token |

La documentación interactiva está en `/docs`.

## Patrones de diseño

Seis patrones GoF (2 creacionales, 2 estructurales, 2 de comportamiento), con código real, prueba unitaria y diagrama UML en [`docs/uml/patrones.md`](docs/uml/patrones.md).

| Tipo | Patrón | Archivo | Caso de uso | Test | UML |
| --- | --- | --- | --- | --- | --- |
| Creacional | Abstract Factory | `apps/api/src/velmora/patterns/abstract_factory.py` | Familias de acceso usuario/admin: datos y storage con privilegios distintos | `test_abstract_factory_creates_two_related_products`, `test_admin_factory_requires_secret` | [Diagrama](docs/uml/patrones.md#abstract-factory-creacional) |
| Creacional | Builder | `apps/api/src/velmora/patterns/builder.py` | Construye `InvestmentQuery` con filtros validados e inmutables | `test_builder_accumulates_filters_without_mutating`, `test_builder_rejects_invalid_ranges` | [Diagrama](docs/uml/patrones.md#builder-creacional) |
| Estructural | Adapter | `apps/api/src/velmora/patterns/adapter.py` | `StorageAccess` normaliza Supabase Storage frente a una fuente en memoria | `test_storage_privileges_differ_between_families` | [Diagrama](docs/uml/patrones.md#adapter-estructural) |
| Estructural | Decorator | `apps/api/src/velmora/patterns/decorator.py` | Logging y caché por ámbito sobre `InvestmentRepository` | `test_cache_decorator_is_scoped_per_user` | [Diagrama](docs/uml/patrones.md#decorator-estructural) |
| Comportamiento | Strategy | `apps/api/src/velmora/patterns/strategy.py` | Recomendación conservadora/moderada/agresiva según perfil de riesgo | `test_strategy_can_change_at_runtime`, `test_recommendations_change_with_profile` | [Diagrama](docs/uml/patrones.md#strategy-comportamiento) |
| Comportamiento | Observer | `apps/api/src/velmora/patterns/observer.py` | `LessonCompleted` notifica progreso y actividad | `test_observer_notifies_all_subscribers`, `test_lesson_completion_notifies_observers` | [Diagrama](docs/uml/patrones.md#observer-comportamiento) |

### Abstract Factory

Crea familias coherentes de acceso: `UserAccessFactory` usa el JWT del usuario y `AdminAccessFactory` la clave secreta del servidor. Así la API no decide credenciales ni privilegios en cada endpoint.

### Builder

`InvestmentQueryBuilder` construye filtros de inversión paso a paso, valida montos y rangos, y devuelve un `InvestmentQuery` inmutable. Centraliza las reglas de filtrado sin crear objetos a medias.

### Adapter

`StorageAccess` ofrece una interfaz única para obtener URLs públicas. `SupabaseStorageAdapter` la implementa con Supabase Storage y `InMemoryStorageAdapter` con una fuente local para pruebas.

### Decorator

`LoggingRepositoryDecorator` añade trazas y `CachingRepositoryDecorator` memoriza consultas por usuario y filtros. Ambos se apilan sobre `InvestmentRepository` sin modificar su código.

### Strategy

`RecommendationContext` selecciona entre estrategias conservadora, moderada y agresiva según el `profile`. Cada estrategia puntúa el riesgo de forma distinta y puede cambiar en tiempo de ejecución.

### Observer

`LessonCompletedPublisher` notifica el evento `LessonCompleted` a `ProgressObserver` y `ActivityObserver`. Al completar una lección se registra progreso y actividad sin acoplar el servicio a cada efecto.

Patrones complementarios: Repository, Dependency Injection (`Depends`), Service Layer y Provider de React. No se contabilizan dentro del requisito 2+2+2.

## Arquitectura y seguridad

- React llama a FastAPI usando `VITE_API_URL`; Supabase Auth se usa en el navegador solo con la publishable key.
- FastAPI verifica JWT con JWKS (firma, `exp`, `iss`, `aud`) antes de propagar el token a PostgREST.
- Los repositorios de usuario usan el JWT de la petición, por lo que RLS se evalúa con la identidad correcta. El cliente administrativo usa `SUPABASE_SECRET_KEY` únicamente en servidor.
- Las migraciones aplican RLS a todas las tablas de `public`; el contenido publicado es legible por anónimos y los datos privados por su propietario.
- Storage separa `avatars` (privado) de `content-images` (público).

## Despliegue

Dos proyectos de Vercel sobre el mismo repositorio:

| Proyecto | Root Directory | Salida | URL |
| --- | --- | --- | --- |
| `velmora-web` | `apps/web` | Vite (`dist/`) | https://velmora-ten-pied.vercel.app/ |
| `velmora-api` | `apps/api` | Vercel Functions (`api/index.py`) | https://velmora-woad.vercel.app/ |

El proyecto Supabase remoto es `Velmora` (ref `qkhqafhsixdvvokacpvn`). La URL base para `SUPABASE_URL` y `VITE_SUPABASE_URL` es `https://qkhqafhsixdvvokacpvn.supabase.co`; el endpoint REST es `https://qkhqafhsixdvvokacpvn.supabase.co/rest/v1/`.

`CORS_ORIGINS` en la API debe incluir exactamente el origen de la web, actualmente `https://velmora-ten-pied.vercel.app`.

`main` despliega a producción y las previsualizaciones de PR se usan solo para validar interfaz y compilación. La migración y el seed ya están aplicados al proyecto remoto; las pruebas RLS pasan en local y la verificación remota devuelve los mismos resultados.

## Documentación

- [ADRs](docs/adr/README.md)
- [Diagramas UML](docs/uml/patrones.md)
- [Código de conducta](CODE_OF_CONDUCT.md)
- [Licencia MIT](LICENSE)

## Estado

Implementación funcional y verificada: API, web, Supabase local y remoto, RLS, seis patrones GoF y pruebas. En Vercel, la web responde 200 y la API responde 200 en `/health`, categorías, lecciones, inversiones y recomendaciones, con `Access-Control-Allow-Origin` para el origen de la web. La migración y el seed remotos están aplicados.

## Advertencia

VELMORA tiene fines educativos. No garantiza rendimientos ni constituye asesoría financiera.
