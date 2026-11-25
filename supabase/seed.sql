insert into public.categories (name, slug, description, published)
values
  ('Depósitos a término fijo', 'cdt', 'Depósitos con tasa y plazo definidos.', true),
  ('Fondos de inversión colectiva', 'fic', 'Carteras administradas por una sociedad fiduciaria.', true),
  ('Fondos de capital privado', 'fcp', 'Inversiones en empresas no listadas.', true),
  ('Renta variable', 'acciones', 'Acciones listadas en la bolsa colombiana.', true),
  ('Renta fija pública', 'tes', 'Títulos de deuda pública del Estado.', true),
  ('Criptoactivos', 'cripto', 'Activos digitales de alta volatilidad.', true)
on conflict (slug) do nothing;

insert into public.investments (
  category_id, name, slug, summary, minimum_amount, risk_level, horizon_months, published
)
select c.id, v.name, v.slug, v.summary, v.minimum_amount, v.risk_level, v.horizon_months, true
from (
  values
    ('cdt', 'CDT bancario', 'cdt-bancario', 'Tasa fija pactada al inicio del plazo.', 1000000, 'bajo', 12),
    ('fic', 'FIC conservador', 'fic-conservador', 'Fondo colectivo con enfoque conservador.', 500000, 'bajo', 12),
    ('fcp', 'Fondo de capital privado', 'fcp-inversion', 'Participaciones en empresas privadas.', 50000000, 'alto', 60),
    ('acciones', 'Acciones de bolsa', 'acciones-bolsa', 'Compra de acciones en el mercado público.', 100000, 'alto', 36),
    ('tes', 'TES renta fija', 'tes-renta-fija', 'Bonos del Estado colombiano.', 100000, 'bajo', 24),
    ('cripto', 'Criptoactivo', 'cripto-activo', 'Activo digital con alta volatilidad.', 50000, 'alto', 12)
) as v(category_slug, name, slug, summary, minimum_amount, risk_level, horizon_months)
join public.categories c on c.slug = v.category_slug
on conflict (slug) do nothing;

insert into public.lessons (title, slug, content, published)
values
  ('Qué es una inversión', 'que-es-una-inversion', 'Introducción al concepto de inversión y su diferencia con el ahorro.', true),
  ('Riesgo y rentabilidad', 'riesgo-y-rentabilidad', 'Relación entre riesgo, plazo y rentabilidad esperada.', true),
  ('Cómo comparar alternativas', 'comparar-alternativas', 'Criterios para comparar opciones según perfil y objetivos.', true)
on conflict (slug) do nothing;
