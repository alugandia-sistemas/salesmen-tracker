#!/usr/bin/env sh
: "${PORT:=3000}"
# opcional: log simple
echo "Starting static server on 0.0.0.0:${PORT}"
exec npx serve -s dist --listen "tcp://0.0.0.0:${PORT}"
