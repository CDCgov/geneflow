# migration 20180122-01
#
# Change name of map_template column in step table
#

from yoyo import step
step("ALTER TABLE step CHANGE COLUMN map_template template TEXT")


