-- FIA Resource Ledger
-- Authoritative schema for API and LLM quota tracking
-- This file is FINAL and replayable
-- RLS is enabled intentionally (backend access via service key only)

CREATE TABLE IF NOT EXISTS public.resource_ledger (
    resource_name TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL CHECK (resource_type IN ('api', 'llm')),
    used_units NUMERIC NOT NULL CHECK (used_units >= 0),
    max_units NUMERIC NOT NULL CHECK (max_units > 0),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enforce Row Level Security to block public access
ALTER TABLE public.resource_ledger
ENABLE ROW LEVEL SECURITY;
