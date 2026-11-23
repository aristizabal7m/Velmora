# ADR-001: Utilizar un monorepo para VELMORA

- **Fecha:** 2026-11-22
- **Estado:** Propuesto
- **Decisores:** Equipo de VELMORA

## Contexto

VELMORA se compondrá de una API Python (FastAPI), una interfaz React/TypeScript, migraciones y pruebas Supabase, pruebas automáticas y documentación del proyecto universitario. Los cambios funcionales suelen requerir ajustar más de una capa.

## Decisión

Mantener todo en **un único repositorio GitHub** (`velmora`) con esta estructura objetivo:

```text
velmora/
├── apps/
│   ├── api/
│   │   ├── src/velmora/{main.py,core,api/v1,domain,repositories,services,patterns,db}
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── .env.example
│   └── web/
│       ├── src/{app,components,features,lib}
│       ├── package.json
│       └── .env.example
├── supabase/{migrations,seed.sql,tests}
├── .github/workflows/ci.yml
└── docs/adr/
```

Las rutas de ejemplo son conceptuales; durante la Fase 3 se crearán directorios reales, archivos `__init__.py` y el código de arranque necesario. Los despliegues y trabajos de CI operarán desde sus directorios correspondientes.

## Alternativas consideradas

1. **Repositorios separados:** aislamiento sencillo, pero más coordinación entre cambios de API, UI y base de datos.
2. **Un backend con plantillas HTML:** menos complejidad, pero limita el objetivo de practicar React/TypeScript.

## Consecuencias

- **Ventajas:** historial único, PRs coordinadas, documentación y migraciones alineadas, configuración común de CI.
- **Costos:** configuración de rutas de trabajo y cachés por aplicación; commits pueden disparar varias pipelines/despliegues; hay que cuidar qué secretos usa cada aplicación.
- **Regla:** credenciales, `.env` reales, claves secretas y artefactos de build nunca se versionan.

## Verificación

- Una persona puede clonar el repositorio e iniciar API y web siguiendo el README.
- Un PR puede modificar API, web y migraciones de forma trazable.
- Cada proyecto de Vercel identifica su `Root Directory` correcto.

## Referencias

- https://vercel.com/docs/monorepos
