-- Taska «Моя команда»: общие доски.
-- Как применить: Supabase Dashboard -> SQL Editor -> New query -> вставить ВЕСЬ файл -> Run.

create table if not exists public.teams (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create table if not exists public.team_members (
  team_id uuid not null references public.teams(id) on delete cascade,
  email text not null,
  user_id uuid,
  role text not null default 'member',
  created_at timestamptz not null default now(),
  primary key (team_id, email)
);

create table if not exists public.team_boards (
  team_id uuid primary key references public.teams(id) on delete cascade,
  data jsonb,
  updated_at timestamptz not null default now()
);

alter table public.teams enable row level security;
alter table public.team_members enable row level security;
alter table public.team_boards enable row level security;

-- Участник = владелец команды ИЛИ его email/uid есть в team_members.
-- security definer нужен, чтобы политики team_members не зациклились сами на себе.
create or replace function public.is_team_member(t uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from teams where id = t and owner_id = auth.uid())
      or exists(select 1 from team_members m where m.team_id = t
                and (m.user_id = auth.uid() or lower(m.email) = lower(coalesce(auth.jwt()->>'email',''))));
$$;

drop policy if exists teams_select on public.teams;
create policy teams_select on public.teams for select using (public.is_team_member(id));
drop policy if exists teams_insert on public.teams;
create policy teams_insert on public.teams for insert with check (owner_id = auth.uid());
drop policy if exists teams_update on public.teams;
create policy teams_update on public.teams for update using (owner_id = auth.uid());
drop policy if exists teams_delete on public.teams;
create policy teams_delete on public.teams for delete using (owner_id = auth.uid());

drop policy if exists tm_select on public.team_members;
create policy tm_select on public.team_members for select using (public.is_team_member(team_id));
drop policy if exists tm_insert on public.team_members;
create policy tm_insert on public.team_members for insert
  with check (exists(select 1 from public.teams where id = team_id and owner_id = auth.uid()));
drop policy if exists tm_delete on public.team_members;
create policy tm_delete on public.team_members for delete
  using (exists(select 1 from public.teams where id = team_id and owner_id = auth.uid()));

drop policy if exists tb_select on public.team_boards;
create policy tb_select on public.team_boards for select using (public.is_team_member(team_id));
drop policy if exists tb_insert on public.team_boards;
create policy tb_insert on public.team_boards for insert with check (public.is_team_member(team_id));
drop policy if exists tb_update on public.team_boards;
create policy tb_update on public.team_boards for update using (public.is_team_member(team_id));
