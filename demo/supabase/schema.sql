-- ARGUS demo: stored report runs (shareable links + usage stats)
create table if not exists demos (
  id uuid primary key default gen_random_uuid(),
  query text not null check (char_length(query) between 1 and 500),
  mode text not null check (mode in ('quick','compare','deep','platform','timeboxed','regional','narrow')),
  plan jsonb not null default '{}',
  report_md text not null default '',
  created_at timestamptz not null default now()
);

alter table demos enable row level security;

-- Public read: anyone with the link can view a shared report.
create policy "public read demos"
  on demos for select to anon using (true);

-- No public insert: only the serverless API (service_role) writes.
-- (Do NOT add an insert policy for anon.)
