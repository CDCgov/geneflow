# migration 20180713-01
#
# Remove type field from workflow and app tables.
# Add execution context and method to step and job tables.
#

from yoyo import step
step("ALTER TABLE workflow DROP type")
step("ALTER TABLE app DROP type")
step("ALTER TABLE step ADD COLUMN exec_context VARCHAR(256) NOT NULL DEFAULT 'local'")
step("ALTER TABLE step ADD COLUMN exec_method VARCHAR(256) NOT NULL DEFAULT 'auto'")
step("ALTER TABLE job ADD COLUMN exec_context TEXT NOT NULL DEFAULT ''")
step("ALTER TABLE job ADD COLUMN exec_method TEXT NOT NULL DEFAULT ''")


