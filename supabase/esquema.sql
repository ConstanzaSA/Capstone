create table if not exists public.integrantes (
 id text primary key, nombre text not null, rol text default '',
 fecha_actualizacion timestamptz default now()
);
create table if not exists public.tareas (
 id text primary key, titulo text not null, descripcion text default '',
 responsable_id text references public.integrantes(id) on delete set null,
 fecha_entrega date null, prioridad text not null default 'Baja',
 estado text not null default 'Pendiente',
 avance integer not null default 0 check (avance between 0 and 100),
 fecha_creacion timestamptz default now(), fecha_actualizacion timestamptz default now()
);
create table if not exists public.historial (
 id text primary key, fecha timestamptz not null default now(),
 accion text not null, tarea_id text null, tarea text not null, detalle text default ''
);
create table if not exists public.configuracion (
 clave text primary key, valor text default '', fecha_actualizacion timestamptz default now()
);
insert into public.integrantes(id,nombre,rol) values
('integrante_1','Integrante 1','Mecánica'),('integrante_2','Integrante 2','Electrónica'),
('integrante_3','Integrante 3','Programación'),('integrante_4','Integrante 4','Control')
on conflict(id) do nothing;
insert into public.configuracion(clave,valor) values
('nombre_proyecto','Capstone Robótica'),('proxima_entrega','')
on conflict(clave) do nothing;
alter table public.integrantes enable row level security;
alter table public.tareas enable row level security;
alter table public.historial enable row level security;
alter table public.configuracion enable row level security;
