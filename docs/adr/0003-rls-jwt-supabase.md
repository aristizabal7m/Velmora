# ADR-003: Autenticación JWT, autorización con RLS y mínimos privilegios en Supabase

- **Fecha:** 2026-11-22
- **Estado:** Aceptado
- **Decisores:** Equipo de VELMORA

## Contexto

VELMORA almacenará perfiles, progreso y marcadores privados por usuario, y contenidos consultables públicamente. React realizará inicio de sesión por Supabase Auth y llamará a FastAPI. Se deben evitar accesos cruzados entre cuentas y exposición de credenciales administrativas.

## Decisión

1. Usar **Supabase Auth** con claves de firma asimétricas para JWT cuando esté disponible/configurado; en FastAPI verificar firma con JWKS, expiración, emisor y audiencia, nunca simplemente decodificar sin verificar. Implementar una dependencia de autenticación reutilizable; devolver `401` para credenciales ausentes o inválidas y `403` cuando falten permisos.
2. Aplicar **RLS** a todas las tablas de `public`: políticas `SELECT` público (solo contenido publicado) para `categories`, `investments`, `lessons`; políticas por propietario (`auth.uid() = user_id`) para `profiles`, `user_progress`, `bookmarks`, según la operación. Evitar que un usuario pueda editar columnas privilegiadas, como `role`, mediante GRANTs y/o esquema separado con control de acceso.
3. Para consultas por usuario desde el backend, crear un **cliente Supabase con publishable key y JWT del usuario**, propagado por petición a la API de datos (PostgREST). De este modo el motor de Supabase puede evaluar las políticas RLS en el contexto correcto.
4. Mantener un **cliente administrativo distinto**, con `sb_secret_...` (o `service_role` legado si fuera imprescindible), solo en un entorno de servidor seguro y después de autorizar explícitamente la operación. Nunca entregar estas claves al navegador, a builds Vite o al código de la app móvil.
5. El **transaction pooler de PostgreSQL** será una opción solo para conexiones SQL necesarias en trabajos internos o casos justificados; conectarse mediante un usuario privilegiado a PostgreSQL no propaga automáticamente el JWT de Supabase ni hace cumplir las políticas de usuario. Las migraciones se ejecutarán desde CLI/CI con credenciales seguras, usando el método de conexión apropiado.
6. Limitar CORS a orígenes conocidos. Configurar rutas de redirección Auth para local y producción. Las políticas de Storage separarán `avatars` privado de `content-images` público.
7. Registrar errores y eventos sin tokens JWT, contraseñas, claves, cookies de sesión ni datos sensibles.

## Alternativas consideradas

- **Autorizar solo en FastAPI sin RLS:** menos políticas de SQL, pero una sola omisión en un endpoint podría exponer información.
- **Usar siempre un cliente con clave admin:** simplifica integración inicial, pero todas las llamadas pasarían por alto RLS.
- **Conexión PostgreSQL con privilegios de sistema para todo:** complejidad adicional para establecer contexto de identidad real y riesgo de exposición entre usuarios.

## Consecuencias

- **Ventajas:** defensa en profundidad, aislamiento por usuario y despliegue con permisos mínimos.
- **Costos:** pruebas de políticas RLS, gestión cuidadosa de sesiones, refresh tokens y configuración de clientes.
- **Riesgos:** no asumir que un JWT válido implica autorización a cualquier recurso; el servidor y las políticas deben verificar la propiedad/rol.

## Verificación

- `supabase/tests/rls.sql` verifica con pgTAP que un usuario no puede modificar progreso/marcadores ajenos y que el anónimo solo lee contenido publicado: `./node_modules/.bin/supabase test db` → 7 pruebas en verde.
- `apps/api/tests/test_api.py` comprueba 401 en rutas protegidas, 403 para un usuario estándar en ruta admin y que `/auth/me` no devuelve el token.
- `core/security.py` verifica firma JWKS, expiración, emisor y audiencia antes de aceptar un JWT.
- `SUPABASE_SECRET_KEY` solo se lee desde el servidor en `AdminAccessFactory`; el bundle web usa exclusivamente la publishable key.
- Storage separa `avatars` (privado) de `content-images` (público) y `UserStorageAccess` bloquea avatares.

## Referencias

- https://supabase.com/docs/guides/auth/jwts
- https://supabase.com/docs/guides/auth/signing-keys
- https://supabase.com/docs/guides/database/postgres/row-level-security
- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/docs/guides/database/connecting-to-postgres
