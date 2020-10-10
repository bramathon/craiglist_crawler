CREATE TABLE IF NOT EXISTS "listings" (
  "date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT,
  "body" TEXT,
  "metro" TEXT
);
CREATE INDEX listings_id on listings (id);
CREATE INDEX listings_date on listings (id,date);
CREATE INDEX listings_date_metro on listings (id,date,metro);
