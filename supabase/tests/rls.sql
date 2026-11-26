begin;
set search_path = public, extensions;
select extensions.plan(7);

create schema velmora_test;
grant usage on schema velmora_test to authenticated, anon;

create function velmora_test.create_user(user_id uuid, email text)
returns uuid
language plpgsql
security definer
set search_path = public, extensions
as $$
begin
  insert into auth.users (
    id, aud, role, email, encrypted_password, email_confirmed_at,
    created_at, updated_at, raw_user_meta_data, raw_app_meta_data
  )
  values (
    user_id, 'authenticated', 'authenticated', email,
    crypt('Test1234!', gen_salt('bf')), now(), now(), now(),
    '{}'::jsonb, '{"provider":"email","providers":["email"]}'::jsonb
  );
  return user_id;
end;
$$;

create function velmora_test.authenticate(user_id uuid)
returns void
language sql
as $$
  select set_config('request.jwt.claim.sub', user_id::text, true);
  select set_config('request.jwt.claim.role', 'authenticated', true);
  select set_config('role', 'authenticated', true);
$$;

create function velmora_test.anonymous()
returns void
language sql
as $$
  select set_config('request.jwt.claim.sub', '', true);
  select set_config('role', 'anon', true);
$$;

select velmora_test.create_user(
  '11111111-1111-4111-8111-111111111111'::uuid,
  'user_a@example.com'
) as user_a;
select velmora_test.create_user(
  '22222222-2222-4222-8222-222222222222'::uuid,
  'user_b@example.com'
) as user_b;

insert into public.investments (name, slug, minimum_amount, risk_level, published)
values
  ('Pública de prueba', 'publica-prueba', 100000, 'bajo', true),
  ('Oculta de prueba', 'oculta-prueba', 200000, 'medio', false);

select velmora_test.authenticate('11111111-1111-4111-8111-111111111111'::uuid);
insert into public.bookmarks (user_id, investment_id)
select auth.uid(), id
from public.investments
where slug = 'publica-prueba';

select extensions.is(
  (select count(*)::int from public.bookmarks),
  1,
  'el usuario ve sus propios marcadores'
);

select velmora_test.authenticate('22222222-2222-4222-8222-222222222222'::uuid);
select extensions.is(
  (select count(*)::int from public.bookmarks),
  0,
  'otro usuario no ve marcadores ajenos'
);

select extensions.throws_ok(
  format(
    $sql$
      insert into public.bookmarks (user_id, investment_id)
      values ('%s', (select id from public.investments where slug = 'publica-prueba'))
    $sql$,
    '11111111-1111-4111-8111-111111111111'::uuid
  ),
  '42501',
  null::text,
  'un usuario no puede crear marcadores para otro usuario'
);

select velmora_test.authenticate('11111111-1111-4111-8111-111111111111'::uuid);
select extensions.throws_ok(
  $sql$ update public.profiles set role = 'admin' where id = auth.uid() $sql$,
  '42501',
  null::text,
  'un usuario no puede asignarse el rol admin'
);

select velmora_test.anonymous();
select extensions.is(
  (select count(*)::int from public.investments where slug = 'publica-prueba'),
  1,
  'el anónimo ve contenido publicado'
);

select extensions.is(
  (select count(*)::int from public.investments where slug = 'oculta-prueba'),
  0,
  'el anónimo no ve contenido sin publicar'
);

select extensions.throws_ok(
  $sql$ select count(*) from public.profiles $sql$,
  '42501',
  null::text,
  'el anónimo no puede consultar perfiles'
);

select * from extensions.finish();
rollback;
