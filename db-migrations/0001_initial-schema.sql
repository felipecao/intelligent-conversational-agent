CREATE TYPE issue_status AS ENUM (
    'open',
    'in_progress',
    'waiting_on_customer',
    'resolved',
    'closed'
);

CREATE TYPE issue_category AS ENUM (
    'billing',
    'shipping',
    'product_defect',
    'account',
    'technical_support'
);

CREATE TYPE issue_urgency AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TABLE IF NOT EXISTS orders (
    id uuid PRIMARY KEY,
    number character varying NOT NULL,
    po_number character varying NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS issues (
    id uuid PRIMARY KEY,
    number character varying NOT NULL,
    description character varying NOT NULL,
    order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    category issue_category NULL,
    urgency issue_urgency NULL,
    status issue_status NOT NULL,
    conversation_summary character varying NULL
);

CREATE TABLE IF NOT EXISTS chats (
    id uuid PRIMARY KEY,
    title character varying NOT NULL,
    chat_history jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
