SELECT id, customer_id, created_at, total
FROM (
    SELECT
        id,
        customer_id,
        created_at,
        total,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            -- Use id as a tie-breaker so equal timestamps still have one deterministic winner.
            ORDER BY created_at DESC, id DESC
        ) AS row_num
    FROM orders
) ranked_orders
WHERE row_num = 1;
