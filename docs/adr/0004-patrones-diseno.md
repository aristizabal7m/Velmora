# ADR-004: Patrones de diseño que demostrará VELMORA

- **Fecha:** 2026-11-22
- **Estado:** Aceptado
- **Decisores:** Equipo de VELMORA

## Contexto

La asignatura exige **al menos dos patrones GoF creacionales, dos estructurales y dos de comportamiento**. El proyecto también requiere una arquitectura testeable y compatible con FastAPI, React y Supabase. Los patrones deben ser visibles y justificables mediante código y pruebas, no solo nombres de clases.

## Decisión

### Seis patrones GoF evaluables

| Tipo | Patrón | Caso de uso | Evidencia prevista |
| --- | --- | --- | --- |
| Creacional | **Abstract Factory** | `SupabaseAccessFactory`: familias de colaboradores (`data_access` y `storage_access`) para contexto autenticado de usuario vs. administración segura; cada familia debe crear al menos dos productos relacionados | Interfaces de fábrica y productos, dos fábricas concretas, pruebas de aislamiento de privilegios |
| Creacional | **Builder** | `InvestmentQueryBuilder` compone filtros opcionales por monto, riesgo y categoría con validación | Construcción incremental, objeto de consulta inmutable, tests con combinaciones |
| Estructural | **Adapter** | `StorageAdapter` y/o adaptadores de fuentes de inversiones normalizan interfaces de proveedor | Cliente consumiendo una interfaz común y dos implementaciones con distinto origen |
| Estructural | **Decorator** | `LoggingRepositoryDecorator` o `CachingRepositoryDecorator` agrega comportamiento a `InvestmentRepository` sin modificar el repositorio base | Decorator delega a objeto envuelto y preserva interfaz, tests |
| Comportamiento | **Strategy** | `RecommendationStrategy` con variantes conservadora/moderada/agresiva: selección por perfil de riesgo sin prometer rentabilidad | Interfaz, tres estrategias, cambio en ejecución y pruebas |
| Comportamiento | **Observer** | `LessonCompleted` notifica observadores de progreso y actividad; proceso sincrónico inicialmente | Publicador, suscriptores independientes, test que comprueba notificación |

**Observación de diseño:** llamar 'Factory' a una función que selecciona un cliente no es suficiente para demostrar Abstract Factory. Debe crear familias de **productos relacionados**; si la implementación real solo selecciona un único cliente, renombrarla Simple Factory y usar otro caso de Abstract Factory, o rediseñarla conforme a GoF. No permitir que el usuario seleccione un contexto admin mediante un parámetro controlado por el cliente.

### Patrones y técnicas complementarias (no cuentan para el requisito de 2+2+2)

- **Repository (arquitectónico):** `LessonRepository`, `InvestmentRepository` abstraen persistencia.
- **Dependency Injection:** `Depends()` conecta servicios y repositorios en FastAPI. Es un mecanismo de composición, no uno de los seis GoF exigidos.
- **Service Layer / Facade:** `LessonService`, `ProgressService` coordinan casos de uso; una `VelmoraFacade` puede simplificar operaciones complejas si realmente aporta un punto de entrada unificado. *Facade sí es GoF estructural*, pero no se necesita contarlo entre los seis mínimos.
- **Provider (React):** `AuthProvider` comparte el estado de sesión y consume la autenticación Supabase.

## Alternativas consideradas

- **Singleton para cliente Supabase:** no se adopta como requisito; un singleton con estado de usuario podría mezclar identidades entre peticiones de un proceso compartido o serverless.
- **Observer solo en React:** se descarta para la evaluación central porque el profesor exige implementación Python. El Observer evaluable vivirá en Python.
- **Patrones artificiales sin uso real:** se evita agregar clases que no simplifiquen una responsabilidad observada en VELMORA.

## Consecuencias

- Cada patrón contará con responsabilidades claras, diagrama UML, una prueba unitaria y un ejemplo ejecutable.
- Las clases de dominio no dependerán del SDK Supabase siempre que sea razonable, para poder usar repositorios falsos en tests.
- Los módulos de lecciones y progreso representan una ampliación educativa de la idea original y deben marcarse como alcance de la aplicación versión 1, no como una obligación del PDF inicial.

## Verificación

- Seis demostraciones independientes sin necesidad de producción: los seis patrones están en `apps/api/src/velmora/patterns/` y se ejercitan desde endpoints reales o tests unitarios.
- La matriz de `README.md` mapea patrón → archivo → caso de uso → test → diagrama UML.
- `apps/api/tests/test_patterns.py` y `test_api.py` validan Builder, Abstract Factory, Adapter, Decorator, Strategy y Observer; `uv run pytest -q` → 21 pruebas en verde.
- Los diagramas Mermaid están en `docs/uml/patrones.md`.
