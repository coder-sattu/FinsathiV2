CREATE TABLE chat_sessions (
  id          UUID PRIMARY KEY,
  state       TEXT NOT NULL,
  policy_no   TEXT,
  data        JSONB NOT NULL DEFAULT '{}',
  attempts    SMALLINT NOT NULL DEFAULT 0,
  llm_calls   SMALLINT NOT NULL DEFAULT 0,
  editing     BOOLEAN NOT NULL DEFAULT false,
  consent_at  TIMESTAMPTZ,
  guard_hits  SMALLINT NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL
);

CREATE TABLE claim_intimations (
  claim_no        TEXT PRIMARY KEY,
  session_id      UUID REFERENCES chat_sessions(id),
  policy_no       TEXT NOT NULL,
  uhid            TEXT NOT NULL,
  patient_name    TEXT NOT NULL,
  claim_type      TEXT NOT NULL CHECK (claim_type IN ('CASHLESS','REIMBURSEMENT')),
  status          TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','IN_PROCESS','CLOSED')),
  intimator_name  TEXT NOT NULL,
  intimator_email TEXT NOT NULL,
  intimation_type TEXT NOT NULL CHECK (intimation_type IN ('PLANNED','EMERGENCY')),
  doa             DATE NOT NULL,
  doctor_name     TEXT NOT NULL,
  diagnosis_code  TEXT,
  diagnosis_text  TEXT NOT NULL,
  hospital_id     TEXT NOT NULL,
  approx_cost     INTEGER,
  needs_review    BOOLEAN NOT NULL DEFAULT false,
  review_reason   TEXT,
  doc_mismatch    BOOLEAN NOT NULL DEFAULT false,
  payload         JSONB NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_intimations_policy_status ON claim_intimations (policy_no, status);

CREATE TABLE service_requests (
  sr_number  TEXT PRIMARY KEY,
  claim_no   TEXT NOT NULL REFERENCES claim_intimations(claim_no),
  type       TEXT NOT NULL DEFAULT 'DOCUMENT_PENDING',
  status     TEXT NOT NULL DEFAULT 'DOCUMENT_PENDING' CHECK (status IN ('DOCUMENT_PENDING','COMPLETE')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE uploaded_documents (
  id            BIGSERIAL PRIMARY KEY,
  sr_number     TEXT NOT NULL REFERENCES service_requests(sr_number),
  doc_code      TEXT NOT NULL,
  original_name TEXT NOT NULL,
  stored_path   TEXT NOT NULL,
  mime          TEXT NOT NULL,
  size_bytes    INTEGER NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (sr_number, doc_code)
);

CREATE TABLE audit_log (
  id         BIGSERIAL PRIMARY KEY,
  session_id UUID,
  event      TEXT NOT NULL,          -- transition, llm_call, llm_fallback, submit, upload
  from_state TEXT,
  to_state   TEXT,
  detail     JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_extractions (
  id             BIGSERIAL PRIMARY KEY,
  document_id    BIGINT NOT NULL REFERENCES uploaded_documents(id) ON DELETE CASCADE,
  doc_code       TEXT NOT NULL,
  detected_type  TEXT,
  status         TEXT NOT NULL CHECK (status IN ('OK','MISMATCH','WRONG_TYPE','EXTRACTION_FAILED','SKIPPED')),
  fields         JSONB,          -- value/evidence/confidence (PII masked)
  checks         JSONB,          -- per-check tick/warning
  user_accepted  BOOLEAN,
  model          TEXT,
  latency_ms     INTEGER,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE guardrail_events (
  id          BIGSERIAL PRIMARY KEY,
  session_id  UUID,
  stage       TEXT NOT NULL CHECK (stage IN ('INPUT','OUTPUT')),
  code        TEXT NOT NULL,     -- I1..I9, O1..O7
  action      TEXT NOT NULL,     -- BLOCKED, MASKED, DROPPED, RETRIED, FALLBACK, FLAGGED
  snippet     TEXT,              -- masked, max 100 chars
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_guard_session ON guardrail_events (session_id);

CREATE SEQUENCE claim_no_seq START 100;
CREATE SEQUENCE sr_no_seq START 100;
