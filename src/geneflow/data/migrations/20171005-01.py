# migration 20171005-01
#
# Add job step detail to job_step table
# Update job table column names
#

from yoyo import step
step("ALTER TABLE job_step ADD COLUMN detail TEXT AFTER status")
step("ALTER TABLE job CHANGE COLUMN storage work_uri VARCHAR(256) NOT NULL DEFAULT ''")
step("ALTER TABLE job CHANGE COLUMN output output_uri VARCHAR(256) NOT NULL DEFAULT ''")

