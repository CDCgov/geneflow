# migration 20180727-01
#
# Add notifications field to job table.
#

from yoyo import step
step("ALTER TABLE job ADD COLUMN notifications TEXT NOT NULL DEFAULT ''")
