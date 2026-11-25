create extension if not exists pgcrypto;

create table public.categories (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  description text,
  published boolean not null default false,
  created_at timestamptz not null default now()
);

create table public.investments (
  id uuid primary key default gen_random_uuid(),
  category_id uuid references public.categories (id) on delete set null,
  name text not null,
  slug text not null unique,
  summary text not null default '',
  minimum_amount numeric(14, 2) not null check (minimum_amount >= 0),
  risk_level text not null check (risk_level in ('bajo', 'medio', 'alto')),
  horizon_months integer check (horizon_months is null or horizon_months > 0),
  published boolean not null default false,
  disclaimer text not null default 'Información educativa; no garantiza rendimientos.',
  created_at timestamptz not null default now()
);

create table public.lessons (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  slug text not null unique,
  content text not null default '',
  published boolean not null default false,
  created_at timestamptz not null default now()
);

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  avatar_url text,
  role text not null default 'user' check (role in ('user', 'admin')),
  risk_profile text check (risk_profile in ('conservador', 'moderado', 'agresivo')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.user_progress (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  lesson_id uuid not null references public.lessons (id) on delete cascade,
  completed_at timestamptz not null default now(),
  unique (user_id, lesson_id)
);

create table public.bookmarks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  investment_id uuid not null references public.investments (id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (user_id, investment_id)
);

create index investments_category_id_idx on public.investments (category_id);
create index investments_published_idx on public.investments (published);
create index investments_risk_level_idx on public.investments (risk_level);
create index user_progress_user_id_idx on public.user_progress (user_id);
create index bookmarks_user_id_idx on public.bookmarks (user_id);

alter table public.categories enable row level security;
alter table public.investments enable row level security;
alter table public.lessons enable row level security;
alter table public.profiles enable row level security;
alter table public.user_progress enable row level security;
alter table public.bookmarks enable row level security;

create policy "Categorías publicadas son legibles por todos"
  on public.categories for select to anon, authenticated
  using (published);

create policy "Inversiones publicadas son legibles por todos"
  on public.investments for select to anon, authenticated
  using (published);

create policy "Lecciones publicadas son legibles por todos"
  on public.lessons for select to anon, authenticated
  using (published);

revoke all on public.profiles from anon, authenticated;
grant select on public.profiles to authenticated;
grant insert (id, display_name, avatar_url, risk_profile) on public.profiles to authenticated;
grant update (display_name, avatar_url, risk_profile, updated_at) on public.profiles to authenticated;

create policy "Cada usuario lee su perfil"
  on public.profiles for select to authenticated
  using (auth.uid() = id);

create policy "Cada usuario crea su perfil"
  on public.profiles for insert to authenticated
  with check (auth.uid() = id);

create policy "Cada usuario actualiza su perfil"
  on public.profiles for update to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);

revoke all on public.user_progress from anon, authenticated;
grant select, insert, delete on public.user_progress to authenticated;

create policy "Cada usuario gestiona su progreso"
  on public.user_progress for all to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

revoke all on public.bookmarks from anon, authenticated;
grant select, insert, delete on public.bookmarks to authenticated;

create policy "Cada usuario gestiona sus marcadores"
  on public.bookmarks for all to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'display_name', ''));
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

insert into storage.buckets (id, name, public)
values ('avatars', 'avatars', false), ('content-images', 'content-images', true)
on conflict (id) do nothing;

create policy "Avatares privados por usuario"
  on storage.objects for all to authenticated
  using (
    bucket_id = 'avatars'
    and (storage.foldername(name))[1] = auth.uid()::text
  )
  with check (
    bucket_id = 'avatars'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy "Imágenes de contenido públicas"
  on storage.objects for select to anon, authenticated
  using (bucket_id = 'content-images');
