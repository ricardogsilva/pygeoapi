# Load test data into postgres DB
# This script is meant to be run on the container that is running the database

DB_USER=${1:-postgres}
DB_PASSWORD=${2:-pass}
DB_NAME=${3:-test}

SQL_SCRIPTS=(
"/data/hotosm_bdi_waterways.sql"
"/data/dummy_data.sql"
)

for sql_script in "${SQL_SCRIPTS[@]}"; do
  psql "postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}" -f "${sql_script}";
done