# migration 20171029-01
#
# Add number column to step table
#

from yoyo import step
step("ALTER TABLE step ADD COLUMN number INTEGER NOT NULL DEFAULT 1 AFTER name")
step("ALTER TABLE step ADD COLUMN letter CHAR NOT NULL DEFAULT '' AFTER number") 

