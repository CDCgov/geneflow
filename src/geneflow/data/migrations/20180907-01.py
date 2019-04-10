# migration 20180907-01
#
# Add repo_uri columns to workflow and apps, add version to app
#

from yoyo import step
step("ALTER TABLE workflow ADD COLUMN repo_uri TEXT NOT NULL DEFAULT ''")
step("ALTER TABLE app ADD COLUMN repo_uri TEXT NOT NULL DEFAULT ''")
step("ALTER TABLE app ADD COLUMN version VARCHAR(32) NOT NULL DEFAULT ''")


