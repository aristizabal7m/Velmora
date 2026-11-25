# Diagramas UML de los patrones GoF

Los diagramas están en Mermaid y se renderizan directamente en GitHub. Cada sección corresponde a un patrón implementado en `apps/api/src/velmora/patterns/` y verificado en `apps/api/tests/test_patterns.py`.

## Abstract Factory (creacional)

```mermaid
classDiagram
    class AccessFactory {
        <<abstract>>
        +create_data_access() DataAccess
        +create_storage_access() StorageAccess
    }
    class UserAccessFactory {
        -jwt: str
        +create_data_access() UserDataAccess
        +create_storage_access() UserStorageAccess
    }
    class AdminAccessFactory {
        -secret_key: str
        +create_data_access() AdminDataAccess
        +create_storage_access() AdminStorageAccess
    }
    class DataAccess {
        <<interface>>
        +list_investments(query) list
    }
    class StorageAccess {
        <<interface>>
        +public_url(bucket, path) str
    }
    class UserDataAccess
    class AdminDataAccess
    class UserStorageAccess
    class AdminStorageAccess

    AccessFactory <|-- UserAccessFactory
    AccessFactory <|-- AdminAccessFactory
    DataAccess <|.. UserDataAccess
    DataAccess <|.. AdminDataAccess
    StorageAccess <|.. UserStorageAccess
    StorageAccess <|.. AdminStorageAccess
    UserAccessFactory ..> UserDataAccess : crea
    UserAccessFactory ..> UserStorageAccess : crea
    AdminAccessFactory ..> AdminDataAccess : crea
    AdminAccessFactory ..> AdminStorageAccess : crea
```

La fábrica de usuario propaga el JWT del solicitante a PostgREST, por lo que RLS se evalúa con su identidad. La fábrica administrativa exige la clave secreta del servidor y no puede ser seleccionada por el cliente.

## Builder (creacional)

```mermaid
classDiagram
    class InvestmentQueryBuilder {
        -query: InvestmentQuery
        +with_risk(level) InvestmentQueryBuilder
        +with_category(slug) InvestmentQueryBuilder
        +with_min_amount(amount) InvestmentQueryBuilder
        +with_max_amount(amount) InvestmentQueryBuilder
        +including_unpublished() InvestmentQueryBuilder
        +build() InvestmentQuery
    }
    class InvestmentQuery {
        +risk_level: RiskLevel
        +category_slug: str
        +min_amount: Decimal
        +max_amount: Decimal
        +published_only: bool
    }

    InvestmentQueryBuilder ..> InvestmentQuery : construye
```

El builder valida que los montos no sean negativos y que el mínimo no supere el máximo. `InvestmentQuery` es inmutable: cada paso usa `model_copy(update=...)`.

## Adapter (estructural)

```mermaid
classDiagram
    class StorageAccess {
        <<interface>>
        +public_url(bucket, path) str
    }
    class SupabaseStorageAdapter {
        -client: Client
        +public_url(bucket, path) str
    }
    class InMemoryStorageAdapter {
        -urls: dict
        +public_url(bucket, path) str
    }
    class UserStorageAccess {
        -storage: StorageAccess
        +public_url(bucket, path) str
    }

    StorageAccess <|.. SupabaseStorageAdapter
    StorageAccess <|.. InMemoryStorageAdapter
    UserStorageAccess o-- StorageAccess : envuelve
```

El adaptador normaliza la API de Storage de Supabase frente a una interfaz simple, permite sustituirla por una implementación en memoria en tests y evita acoplar el servicio al SDK.

## Decorator (estructural)

```mermaid
classDiagram
    class InvestmentRepository {
        <<interface>>
        +list_investments(query) list
        +get_by_slug(slug) Investment
        +list_categories() list
        +list_lessons() list
    }
    class SupabaseInvestmentRepository {
        +list_investments(query) list
        +get_by_slug(slug) Investment
    }
    class LoggingRepositoryDecorator {
        -wrapped: InvestmentRepository
        +list_investments(query) list
        +get_by_slug(slug) Investment
    }
    class CachingRepositoryDecorator {
        -wrapped: InvestmentRepository
        -scope: str
        -cache: dict
        +list_investments(query) list
        +get_by_slug(slug) Investment
    }

    InvestmentRepository <|.. SupabaseInvestmentRepository
    InvestmentRepository <|.. LoggingRepositoryDecorator
    InvestmentRepository <|.. CachingRepositoryDecorator
    LoggingRepositoryDecorator o-- InvestmentRepository : delegación
    CachingRepositoryDecorator o-- InvestmentRepository : delegación
```

La composición se realiza en `decorate(repository, scope, cache=...)`. El repositorio base permanece intacto; los decoradores añaden trazas y caché por ámbito/petición.

## Strategy (comportamiento)

```mermaid
classDiagram
    class RecommendationStrategy {
        <<interface>>
        +profile: RiskProfile
        +score(investment) float
    }
    class ConservativeStrategy
    class ModerateStrategy
    class AggressiveStrategy
    class RecommendationContext {
        -strategy: RecommendationStrategy
        +set_strategy(strategy) void
        +recommend(investments, limit) list
    }
    class RiskProfile {
        <<enumeration>>
        conservador
        moderado
        agresivo
    }

    RecommendationStrategy <|.. ConservativeStrategy
    RecommendationStrategy <|.. ModerateStrategy
    RecommendationStrategy <|.. AggressiveStrategy
    RecommendationContext o-- RecommendationStrategy
    RecommendationStrategy ..> RiskProfile : expone
```

`InvestmentService` cambia la estrategia según `RiskProfile` y devuelve recomendaciones con motivos textuales; no estima ni promete rentabilidad.

## Observer (comportamiento)

```mermaid
classDiagram
    class Observer {
        <<interface>>
        +update(event) void
    }
    class ProgressObserver {
        +update(event) void
    }
    class ActivityObserver {
        +update(event) void
    }
    class LessonCompletedPublisher {
        -observers: list
        +subscribe(observer) void
        +notify(event) void
    }
    class LessonCompleted {
        +lesson_id: UUID
        +user_id: UUID
        +completed_at: datetime
    }

    Observer <|.. ProgressObserver
    Observer <|.. ActivityObserver
    LessonCompletedPublisher o-- Observer : suscriptores
    LessonCompletedPublisher ..> LessonCompleted : notifica
```

Al completar una lección, `ProgressService` publica `LessonCompleted`; el observador de progreso persiste el avance y el de actividad registra el evento, sin que el servicio conozca sus implementaciones.
