# migration 20171113-01
#
# Add documentation_uri column to workflow
#

from yoyo import step
step("ALTER TABLE workflow ADD COLUMN documentation_uri TEXT AFTER username")


