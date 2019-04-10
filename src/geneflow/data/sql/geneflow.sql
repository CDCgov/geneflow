-- workflow schema v20171005-00

drop table if exists workflow;
drop table if exists app;
drop table if exists step;
drop table if exists depend;
drop table if exists job;
drop table if exists job_step;
drop table if exists _yoyo_migration;

create table workflow (
    id char(32) not null,
    name varchar(256) not null,
    description varchar(256) not null default '',
    version varchar(32) not null default '',
    username varchar(32) not null default '',
    inputs text not null default '',
    parameters text not null default '',
    final_output text not null default '',
    type VARCHAR(256) not null default 'local',
    public tinyint not null default 0,
    created timestamp default '0000-00-00 00:00:00',
    modified timestamp default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    primary key (id)
);

create table app (
    id char(32) not null,
    name varchar(256) not null default '',
    description varchar(256) not null default '',
    username varchar(32) not null default '',
    type varchar(256) not null default 'local',
    definition text not null default '',
    inputs text not null default '',
    parameters text not null default '',
    public tinyint not null default 0,
    primary key (id)
);

-- step dependencies
create table depend (
    child_id char(32) not null,
    parent_id char(32) not null,
    primary key (child_id, parent_id)
);

create table step (
    id char(32) not null,
    name varchar(256) not null default '',
    workflow_id char(32) not null,
    app_id char(32) not null,
    folder varchar(256) not null default '',
    regex varchar(256) not null default '',
    expand text not null default '',
    primary key (id)
);

create table job (
    id char(32) not null,
    workflow_id char(32) not null default '',
    name varchar(256) not null default '',
    username varchar(32) not null default '',
    storage varchar(64) not null default '',
    status varchar(32) not null default 'PENDING',
    queued timestamp default CURRENT_TIMESTAMP,
    started timestamp,
    finished timestamp,
    msg varchar(256) not null default '',
    inputs text not null default '',
    parameters text not null default '',
    output varchar(256) not null default '',
    final_output text not null default '',
    primary key (id)
);

create table job_step (
    job_id char(32) not null default '',
    step_id char(32) not null default '',
    status varchar(32) not null default 'PENDING',
    msg varchar(256) not null default '',
    primary key (step_id, job_id)
);


