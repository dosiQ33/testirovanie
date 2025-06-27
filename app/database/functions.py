"""
Project: nam
Created Date: Tuesday January 28th 2025
Author: RaiMX
-----
Copyright (c) 2025 RaiMX
"""

from alembic_utils.pg_function import PGFunction

to_upper = PGFunction(
    schema="public",
    signature="to_upper(some_text text)",
    definition="""
  RETURNS text as
  $$
    SELECT upper(some_text)
  $$ language SQL;
  """,
)
