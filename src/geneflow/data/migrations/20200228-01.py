# migration 20200228-01
#
# Add no_output_hash column to job table
#

from yoyo import step
step("ALTER TABLE job ADD COLUMN no_output_hash TINYINT NOT NULL DEFAULT 0")


