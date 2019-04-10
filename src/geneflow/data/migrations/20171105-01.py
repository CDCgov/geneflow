# migration 20171105-01
#
# Update column names for map/reduce (previously enum)
#

from yoyo import step
step("ALTER TABLE step CHANGE COLUMN folder map_uri VARCHAR(256) NOT NULL DEFAULT ''")
step("ALTER TABLE step CHANGE COLUMN regex map_regex VARCHAR(256) NOT NULL DEFAULT ''")
step("ALTER TABLE step CHANGE COLUMN expand map_template TEXT")


