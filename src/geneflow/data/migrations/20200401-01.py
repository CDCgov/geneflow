# migration 20200401-01
#
# Add apps column to workflow table
# Add exec_parameters column to step and job tables
#

from yoyo import step
step("ALTER TABLE workflow ADD COLUMN apps TEXT NOT NULL DEFAULT ''")
step("ALTER TABLE step ADD COLUMN exec_parameters TEXT NOT NULL DEFAULT ''")
step("ALTER TABLE job ADD COLUMN exec_parameters TEXT NOT NULL DEFAULT ''")
