-- sqlite3 workflow schema    --
-- this schema cannot migrate --

DROP TABLE IF EXISTS workflow;
DROP TABLE IF EXISTS app;
DROP TABLE IF EXISTS step;
DROP TABLE IF EXISTS depend;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS job_step;
DROP TRIGGER IF EXISTS update_workflow;

CREATE TABLE workflow (
    id CHAR(32) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description VARCHAR(256) NOT NULL DEFAULT '',
    version VARCHAR(32) NOT NULL DEFAULT '',
    username VARCHAR(32) NOT NULL DEFAULT '',
    repo_uri TEXT NOT NULL DEFAULT '',
    documentation_uri TEXT NOT NULL DEFAULT '',
    inputs TEXT NOT NULL DEFAULT '',
    parameters TEXT NOT NULL DEFAULT '',
    final_output TEXT NOT NULL DEFAULT '',
    public TINYINT NOT NULL DEFAULT 0,
    enable TINYINT NOT NULL DEFAULT 1,
    created TIMESTAMP DEFAULT '0000-00-00 00:00:00',
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TRIGGER update_workflow
    AFTER UPDATE
    ON workflow
BEGIN
    UPDATE workflow SET modified = CURRENT_TIMESTAMP WHERE id = new.id;
END;

CREATE TABLE app (
    id CHAR(32) NOT NULL,
    name VARCHAR(256) NOT NULL DEFAULT '',
    description VARCHAR(256) NOT NULL DEFAULT '',
    repo_uri TEXT NOT NULL DEFAULT '',
    version VARCHAR(32) NOT NULL DEFAULT '',
    username VARCHAR(32) NOT NULL DEFAULT '',
    definition TEXT NOT NULL DEFAULT '',
    inputs TEXT NOT NULL DEFAULT '',
    parameters TEXT NOT NULL DEFAULT '',
    public TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

-- step dependencies
CREATE TABLE depend (
    child_id CHAR(32) NOT NULL,
    parent_id CHAR(32) NOT NULL,
    PRIMARY KEY (child_id, parent_id)
);

CREATE TABLE step (
    id CHAR(32) NOT NULL,
    name VARCHAR(256) NOT NULL DEFAULT '',
    number INTEGER NOT NULL DEFAULT 1,
    letter CHAR NOT NULL DEFAULT '',
    workflow_id CHAR(32) NOT NULL,
    app_id CHAR(32) NOT NULL,
    map_uri VARCHAR(256) NOT NULL DEFAULT '',
    map_regex VARCHAR(256) NOT NULL DEFAULT '',
    template TEXT NOT NULL DEFAULT '',
    exec_context VARCHAR(256) NOT NULL DEFAULT 'local',
    exec_method VARCHAR(256) NOT NULL DEFAULT 'auto',
    PRIMARY KEY (id)
);

CREATE TABLE job (
    id CHAR(32) NOT NULL,
    workflow_id CHAR(32) NOT NULL DEFAULT '',
    name VARCHAR(256) NOT NULL DEFAULT '',
    username VARCHAR(32) NOT NULL DEFAULT '',
    work_uri VARCHAR(256) NOT NULL DEFAULT '',
    no_output_hash INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    queued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started TIMESTAMP,
    finished TIMESTAMP,
    msg VARCHAR(256) NOT NULL DEFAULT '',
    inputs TEXT NOT NULL DEFAULT '',
    parameters TEXT NOT NULL DEFAULT '',
    output_uri VARCHAR(256) NOT NULL DEFAULT '',
    final_output TEXT NOT NULL DEFAULT '',
    exec_context TEXT NOT NULL DEFAULT '',
    exec_method TEXT NOT NULL DEFAULT '',
    notifications TEXT NOT NULL DEFAULT '[]',
    PRIMARY KEY (id)
);

CREATE TABLE job_step (
    job_id CHAR(32) NOT NULL DEFAULT '',
    step_id CHAR(32) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    detail TEXT NOT NULL DEFAULT '',
    msg VARCHAR(256) NOT NULL DEFAULT '',
    PRIMARY KEY (step_id, job_id)
);


