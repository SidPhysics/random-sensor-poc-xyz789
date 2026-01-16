#!/bin/bash
# Prepare Lambda deployment packages

echo "Preparing Lambda deployment packages..."

# Copy shared module into ingest
echo "Copying shared/ to ingest/shared/"
cp -r shared ingest/

# Copy shared module into query
echo "Copying shared/ to query/shared/"
cp -r shared query/

echo "Lambda packages ready for deployment"
