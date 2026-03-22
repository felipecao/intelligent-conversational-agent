-- Sample data for local development and demos.
-- Depends on 0001_initial-schema.sql (enums issue_status, issue_category, issue_urgency).
-- Insert order: orders, then issues.

INSERT INTO orders (id, number, po_number, created_at, updated_at) VALUES
    ('d0000001-0000-4000-8000-000000000001', 'ORD-2024-1001', 'PO-77821', now() - interval '12 days', now() - interval '1 day'),
    ('d0000001-0000-4000-8000-000000000002', 'ORD-2024-1002', 'PO-77822', now() - interval '5 days', now()),
    ('d0000001-0000-4000-8000-000000000003', 'ORD-2024-1003', 'PO-77823', now() - interval '2 days', now()),
    ('d0000001-0000-4000-8000-000000000004', 'ORD-2024-1004', 'PO-77824', now() - interval '30 days', now() - interval '3 days')
ON CONFLICT (id) DO NOTHING;

INSERT INTO issues (id, number, description, order_id, status, category, urgency) VALUES
    (
        'e0000001-0000-4000-8000-000000000001',
        'ISS-240001',
        'Invoice total does not match the order confirmation email.',
        'd0000001-0000-4000-8000-000000000001',
        'in_progress'::issue_status,
        'billing'::issue_category,
        'medium'::issue_urgency
    ),
    (
        'e0000001-0000-4000-8000-000000000002',
        'ISS-240002',
        'Shipment marked delivered but package not received.',
        'd0000001-0000-4000-8000-000000000002',
        'open'::issue_status,
        'shipping'::issue_category,
        'high'::issue_urgency
    ),
    (
        'e0000001-0000-4000-8000-000000000003',
        'ISS-240003',
        'Login fails after password reset; error code AUTH-1042.',
        'd0000001-0000-4000-8000-000000000003',
        'waiting_on_customer'::issue_status,
        'account'::issue_category,
        'high'::issue_urgency
    ),
    (
        'e0000001-0000-4000-8000-000000000004',
        'ISS-240004',
        'Widget X overheating under normal load within 10 minutes.',
        'd0000001-0000-4000-8000-000000000003',
        'open'::issue_status,
        'product_defect'::issue_category,
        'critical'::issue_urgency
    ),
    (
        'e0000001-0000-4000-8000-000000000005',
        'ISS-240005',
        'API rate limit errors when syncing inventory overnight.',
        'd0000001-0000-4000-8000-000000000004',
        'resolved'::issue_status,
        'technical_support'::issue_category,
        'medium'::issue_urgency
    ),
    (
        'e0000001-0000-4000-8000-000000000006',
        'ISS-240006',
        'Request to merge duplicate accounts under same email domain.',
        'd0000001-0000-4000-8000-000000000001',
        'closed'::issue_status,
        'account'::issue_category,
        'low'::issue_urgency
    )
ON CONFLICT (id) DO NOTHING;
