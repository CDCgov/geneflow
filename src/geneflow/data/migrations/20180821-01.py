# migration 20180821-01
#
# Add enable field to workflow table.
#

from yoyo import step
step("ALTER TABLE workflow ADD COLUMN enable TINYINT NOT NULL DEFAULT 1")
