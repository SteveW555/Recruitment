-- 9. Office Rent & Facilities
-- CSV: expense_id,expense_date,office_location,expense_type,square_feet,price_per_sqft,amount,payment_status,payment_method,notes
CREATE TABLE office_rent_facilities (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    expense_date DATE NOT NULL,
    office_location TEXT NOT NULL,
    expense_type TEXT NOT NULL,
    square_feet INTEGER,
    price_per_sqft NUMERIC(8,2),
    amount NUMERIC(10,2) NOT NULL,
    payment_status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

