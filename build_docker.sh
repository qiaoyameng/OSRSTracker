#!/bin/bash
NAMESPACE="${1:-codebase_b2479_app}"
docker build -t "$NAMESPACE" .