---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Our Supabase app is live and the `orders` table has about 40 million rows. I need to add a `tenant_id` column that is NOT NULL, fill it from `customers.tenant_id`, and add an index on it. How should I write the migration files so the table doesn't lock up while users are placing orders?
