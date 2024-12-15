# STARTUP
# ALLOWED_ORIGINS=http://localhost,http://localhost:8000,http://example.com
APP_DEBUG=False
SQL_DEBUG=False
API_DOCS=True
FRONTEND_ENABLED=True

# LOGGING
LOGGING_LEVEL=INFO

# SERVER OPTION
SERVER_HOST=0.0.0.0
SERVER_PORT=8085
SERVER_WORKERS=4

# DATABASE
# IF with docker -> :////var/lib/telegrapy/
# ELSE -> any
DB_URL=sqlite+aiosqlite:////var/lib/telegrapy/db.sqlite3

# IF SERVER DATABASE
DB_POOL_SIZE=100
DB_POOL_OVERFLOW=20
DB_TIMEOUT=5

# LIMITS (From IP)
# count/time
# example 10/second   (10 per second)
# example 500/minute  (500 per minute)
LIMIT_CREATE_ACCOUNT=3/second
LIMIT_EDIT_ACCOUNT=100/second
LIMIT_CREATE_PAGE=5/second
LIMIT_EDIT_PAGE=10/second

LIMIT_DELETE_PAGE=50/second
LIMIT_ADD_VIEW=1000/second
LIMIT_RESET_TOKEN=500/second
LIMIT_GET_ACCOUNT=1000/second
LIMIT_GET_PAGE=2500/second
LIMIT_GET_PAGES=500/second
