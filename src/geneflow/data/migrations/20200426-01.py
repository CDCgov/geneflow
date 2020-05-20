# migration 20200426-01
#
# Add test column to workflow table
#

from yoyo import step
step("ALTER TABLE workflow ADD COLUMN test TINYINT NOT NULL DEFAULT 0")


