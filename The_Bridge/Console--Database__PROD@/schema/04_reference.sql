-- Reference Data Schema
-- Read-only shared reference data (DEFRA factors, HS codes, etc.)

-- DEFRA Emission Factors
CREATE TABLE reference.defra_factors_v2025 (
    factor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    factor_pack TEXT NOT NULL DEFAULT 'DEFRA-2025',
    mode TEXT NOT NULL, -- truck, air, rail, sea, electricity
    vehicle_class TEXT NOT NULL,
    region TEXT,
    unit TEXT NOT NULL, -- kgCO2e/t.km, kgCO2e/kWh
    co2e_per_unit NUMERIC NOT NULL,
    ttw_share NUMERIC, -- Tank-to-Wheel percentage (0-1)
    wtt_share NUMERIC, -- Well-to-Tank percentage (0-1)
    rf_uplift NUMERIC, -- Radiative Forcing for air freight
    source_table TEXT,
    source_row TEXT,
    methodology_url TEXT,
    valid_from DATE DEFAULT '2025-01-01',
    valid_until DATE,
    notes TEXT
);

-- ICAO Airport Codes
CREATE TABLE reference.icao_airports (
    icao_code TEXT PRIMARY KEY,
    iata_code TEXT,
    airport_name TEXT NOT NULL,
    city TEXT,
    country_code TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    elevation_m INTEGER
);

-- HS Codes (Harmonized System) for commodities
CREATE TABLE reference.hs_codes (
    hs_code TEXT PRIMARY KEY,
    hs_level INTEGER, -- 2, 4, 6, 8 digits
    parent_code TEXT,
    description_en TEXT NOT NULL,
    description_local TEXT,
    unit_of_measure TEXT,
    duty_rate NUMERIC,
    valid_from DATE,
    valid_until DATE
);

-- Country and Region Codes
CREATE TABLE reference.countries (
    country_code TEXT PRIMARY KEY, -- ISO 3166-1 alpha-2
    country_code_alpha3 TEXT UNIQUE, -- ISO 3166-1 alpha-3
    country_name TEXT NOT NULL,
    region TEXT,
    subregion TEXT,
    currency_code TEXT,
    timezone TEXT,
    is_eu BOOLEAN DEFAULT false,
    is_oecd BOOLEAN DEFAULT false
);

-- Currency Exchange Rates
CREATE TABLE reference.exchange_rates (
    rate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency TEXT NOT NULL,
    to_currency TEXT NOT NULL,
    rate NUMERIC NOT NULL,
    rate_date DATE NOT NULL,
    source TEXT,
    UNIQUE(from_currency, to_currency, rate_date)
);

-- Transport Routes and Distances
CREATE TABLE reference.transport_routes (
    route_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_location TEXT NOT NULL,
    to_location TEXT NOT NULL,
    mode TEXT NOT NULL,
    distance_km NUMERIC NOT NULL,
    typical_duration_hours NUMERIC,
    route_type TEXT, -- direct, hub_spoke, multi_modal
    waypoints JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

-- Commodity Carbon Intensities
CREATE TABLE reference.commodity_emissions (
    commodity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    commodity_name TEXT NOT NULL,
    hs_code TEXT REFERENCES reference.hs_codes(hs_code),
    category TEXT,
    lifecycle_stage TEXT, -- production, processing, packaging
    emission_factor NUMERIC NOT NULL,
    unit TEXT NOT NULL, -- kgCO2e/kg, kgCO2e/unit
    source TEXT,
    region TEXT,
    valid_from DATE,
    valid_until DATE
);

-- Insert DEFRA 2025 factors (simplified subset)
INSERT INTO reference.defra_factors_v2025 (mode, vehicle_class, unit, co2e_per_unit, ttw_share, wtt_share, source_table) VALUES
-- Road Transport
('truck', 'Rigid_3.5-7.5t_Euro6', 'kgCO2e/t.km', 0.2651, 0.72, 0.28, 'Freighting goods - HGVs'),
('truck', 'Rigid_7.5-12t_Euro6', 'kgCO2e/t.km', 0.1876, 0.72, 0.28, 'Freighting goods - HGVs'),
('truck', 'Rigid_12-14t_Euro6', 'kgCO2e/t.km', 0.1542, 0.72, 0.28, 'Freighting goods - HGVs'),
('truck', 'Articulated_14-20t_Euro6', 'kgCO2e/t.km', 0.1234, 0.72, 0.28, 'Freighting goods - HGVs'),
('truck', 'Articulated_20-26t_Euro6', 'kgCO2e/t.km', 0.0987, 0.72, 0.28, 'Freighting goods - HGVs'),
('truck', 'Articulated_>33t_Euro6', 'kgCO2e/t.km', 0.0584, 0.72, 0.28, 'Freighting goods - HGVs'),

-- Air Freight
('air', 'Narrowbody_Freighter', 'kgCO2e/t.km', 1.2345, 0.85, 0.15, 'Freighting goods - Air'),
('air', 'Widebody_Freighter', 'kgCO2e/t.km', 0.8983, 0.85, 0.15, 'Freighting goods - Air'),
('air', 'Passenger_Belly_Narrowbody', 'kgCO2e/t.km', 1.5432, 0.85, 0.15, 'Freighting goods - Air'),
('air', 'Passenger_Belly_Widebody', 'kgCO2e/t.km', 1.0234, 0.85, 0.15, 'Freighting goods - Air'),

-- Rail Freight
('rail', 'EU_Freight_Rail_Avg', 'kgCO2e/t.km', 0.0275, 0.65, 0.35, 'Freighting goods - Rail'),
('rail', 'UK_Freight_Rail', 'kgCO2e/t.km', 0.0289, 0.60, 0.40, 'Freighting goods - Rail'),
('rail', 'Electric_Rail', 'kgCO2e/t.km', 0.0198, 0.70, 0.30, 'Freighting goods - Rail'),
('rail', 'Diesel_Rail', 'kgCO2e/t.km', 0.0412, 0.75, 0.25, 'Freighting goods - Rail'),

-- Sea Freight
('ship', 'Container_Ship_Small', 'kgCO2e/t.km', 0.0162, 0.87, 0.13, 'Freighting goods - Sea'),
('ship', 'Container_Ship_Large', 'kgCO2e/t.km', 0.0089, 0.87, 0.13, 'Freighting goods - Sea'),
('ship', 'Bulk_Carrier', 'kgCO2e/t.km', 0.0056, 0.87, 0.13, 'Freighting goods - Sea'),
('ship', 'RoRo_Ferry', 'kgCO2e/t.km', 0.0456, 0.87, 0.13, 'Freighting goods - Sea'),

-- Electricity
('electricity', 'grid_average_uk', 'kgCO2e/kWh', 0.2074, 1.0, 0, 'UK electricity'),
('electricity', 'grid_average_eu', 'kgCO2e/kWh', 0.2765, 1.0, 0, 'EU electricity'),
('electricity', 'grid_average_kenya', 'kgCO2e/kWh', 0.3421, 1.0, 0, 'Kenya electricity'),
('electricity', 'diesel_generator', 'kgCO2e/kWh', 0.7341, 0.85, 0.15, 'Stationary combustion'),
('electricity', 'solar_pv', 'kgCO2e/kWh', 0.0100, 1.0, 0, 'Renewable - Solar'),
('electricity', 'wind', 'kgCO2e/kWh', 0.0120, 1.0, 0, 'Renewable - Wind');

-- Set RF uplift for air freight
UPDATE reference.defra_factors_v2025 
SET rf_uplift = 1.9 
WHERE mode = 'air';

-- Insert sample HS codes for agricultural products
INSERT INTO reference.hs_codes (hs_code, hs_level, description_en, unit_of_measure) VALUES
('0708', 4, 'Leguminous vegetables, shelled or unshelled, fresh or chilled', 'kg'),
('070820', 6, 'Beans (Vigna spp., Phaseolus spp.), fresh or chilled', 'kg'),
('070890', 6, 'Other leguminous vegetables, fresh or chilled', 'kg'),
('0904', 4, 'Pepper of the genus Piper; dried or crushed or ground fruits', 'kg'),
('090411', 6, 'Pepper, neither crushed nor ground', 'kg'),
('0810', 4, 'Other fruit, fresh', 'kg'),
('081090', 6, 'Other fruit, fresh (including passion fruit)', 'kg');

-- Insert key airports
INSERT INTO reference.icao_airports (icao_code, iata_code, airport_name, city, country_code) VALUES
('HKJK', 'NBO', 'Jomo Kenyatta International Airport', 'Nairobi', 'KE'),
('HKEL', 'EDL', 'Eldoret International Airport', 'Eldoret', 'KE'),
('EDDF', 'FRA', 'Frankfurt Airport', 'Frankfurt', 'DE'),
('EDDH', 'HAM', 'Hamburg Airport', 'Hamburg', 'DE'),
('EHAM', 'AMS', 'Amsterdam Airport Schiphol', 'Amsterdam', 'NL'),
('EGLL', 'LHR', 'London Heathrow Airport', 'London', 'GB');

-- Insert countries
INSERT INTO reference.countries (country_code, country_code_alpha3, country_name, region, is_eu) VALUES
('KE', 'KEN', 'Kenya', 'Africa', false),
('DE', 'DEU', 'Germany', 'Europe', true),
('NL', 'NLD', 'Netherlands', 'Europe', true),
('GB', 'GBR', 'United Kingdom', 'Europe', false),
('FR', 'FRA', 'France', 'Europe', true),
('US', 'USA', 'United States', 'Americas', false);

-- Insert sample transport routes
INSERT INTO reference.transport_routes (from_location, to_location, mode, distance_km, typical_duration_hours) VALUES
('Eldoret', 'NBO', 'truck', 320, 6),
('NBO', 'FRA', 'air', 6248, 9),
('FRA', 'Hamburg', 'rail', 493, 4),
('FRA', 'Hamburg', 'truck', 545, 6),
('NBO', 'AMS', 'air', 6517, 9),
('AMS', 'Hamburg', 'truck', 468, 5);

-- Create views for easier access
CREATE VIEW reference.v_defra_transport AS
SELECT 
    mode,
    vehicle_class,
    co2e_per_unit,
    unit,
    ttw_share * co2e_per_unit AS ttw_factor,
    wtt_share * co2e_per_unit AS wtt_factor,
    rf_uplift
FROM reference.defra_factors_v2025
WHERE mode IN ('truck', 'rail', 'air', 'ship');

-- Grant read-only access to reference schema
GRANT USAGE ON SCHEMA reference TO app_reader, app_writer, app_admin, app_agent;
GRANT SELECT ON ALL TABLES IN SCHEMA reference TO app_reader, app_writer, app_admin, app_agent;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA reference TO app_reader, app_writer, app_admin, app_agent;

-- Reference tables are read-only, no RLS needed
-- But we can add update restrictions
CREATE OR REPLACE FUNCTION reference.prevent_modifications()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Reference data is read-only. Contact admin for updates.';
END;
$$ LANGUAGE plpgsql;

-- Apply to all reference tables
CREATE TRIGGER no_insert_defra BEFORE INSERT ON reference.defra_factors_v2025
    FOR EACH ROW EXECUTE FUNCTION reference.prevent_modifications();
CREATE TRIGGER no_update_defra BEFORE UPDATE ON reference.defra_factors_v2025
    FOR EACH ROW EXECUTE FUNCTION reference.prevent_modifications();
CREATE TRIGGER no_delete_defra BEFORE DELETE ON reference.defra_factors_v2025
    FOR EACH ROW EXECUTE FUNCTION reference.prevent_modifications();