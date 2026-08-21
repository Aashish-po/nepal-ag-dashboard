-- Backfill existing NULL data_source values before enforcing NOT NULL
UPDATE yields SET data_source = 'UNKNOWN' WHERE data_source IS NULL;
UPDATE climate SET data_source = 'UNKNOWN' WHERE data_source IS NULL;

-- Districts table
CREATE TABLE districts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  province VARCHAR(50) NOT NULL,
  region VARCHAR(50),  -- Mountain / Hill / Terai
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  population INT,  -- 2021 census estimate
  area_sq_km DECIMAL(10, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for districts
CREATE INDEX idx_districts_name ON districts(name);
CREATE INDEX idx_districts_province ON districts(province);
CREATE INDEX idx_districts_region ON districts(region);

-- Crops table
CREATE TABLE crops (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  fao_code VARCHAR(10),  -- FAOSTAT code (e.g., 'F0312' for cardamom)
  category VARCHAR(50),  -- 'Cereal' | 'Vegetable' | 'Spice' | 'Fruit' | 'Export'
  unit VARCHAR(20) DEFAULT 'MT',  -- Metric tons
  is_export_crop BOOLEAN DEFAULT FALSE,
  is_subsistence BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Yields table (fact table)
CREATE TABLE yields (
  id BIGSERIAL PRIMARY KEY,
  district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  crop_id INT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
  year INT NOT NULL,
  production_mt DECIMAL(15, 2),  -- Metric tons (total output)
  area_harvested_ha DECIMAL(15, 2),  -- Hectares
  yield_kg_ha DECIMAL(10, 2),  -- Computed: (production_mt * 1000) / area_harvested_ha
  data_source VARCHAR(100) NOT NULL DEFAULT 'UNKNOWN',  -- 'FAOSTAT' | 'MoALD' | 'Regional'
  data_quality VARCHAR(20) DEFAULT 'Estimated',  -- 'Official' | 'Estimated' | 'Interpolated'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(district_id, crop_id, year, data_source)
);

-- Indexes for yields
CREATE INDEX idx_yields_district_year ON yields(district_id, year DESC);
CREATE INDEX idx_yields_crop_year ON yields(crop_id, year DESC);
CREATE INDEX idx_yields_data_source ON yields(data_source);

-- Climate table (fact table)
CREATE TABLE climate (
  id BIGSERIAL PRIMARY KEY,
  district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  observation_date DATE NOT NULL,  -- First day of month
  rainfall_mm DECIMAL(10, 2),  -- Monthly total (mm)
  temperature_min_c DECIMAL(5, 2),  -- Monthly average min (°C)
  temperature_max_c DECIMAL(5, 2),  -- Monthly average max (°C)
  temperature_mean_c DECIMAL(5, 2),  -- Computed: (min + max) / 2
  solar_radiation_mj_m2 DECIMAL(8, 2),  -- Monthly total (MJ/m²)
  data_source VARCHAR(100) NOT NULL DEFAULT 'UNKNOWN',  -- 'NASA POWER' | 'CHIRPS' | 'Regional'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(district_id, observation_date, data_source)
);

-- Indexes for climate
CREATE INDEX idx_climate_district_date ON climate(district_id, observation_date DESC);
CREATE INDEX idx_climate_data_source ON climate(data_source);

-- Export crops table (dimension table)
CREATE TABLE export_crops (
  id SERIAL PRIMARY KEY,
  crop_id INT NOT NULL UNIQUE REFERENCES crops(id) ON DELETE CASCADE,
  main_export_countries TEXT[],  -- e.g., ARRAY['India', 'Japan', 'EU']
  avg_price_usd_per_mt DECIMAL(10, 2),  -- Recent avg price
  export_season_start_month INT,  -- e.g., 9 for cardamom (Sept harvest)
  export_season_end_month INT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Commercialization index table (computed table)
CREATE TABLE commercialization_index (
  id SERIAL PRIMARY KEY,
  district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  year INT NOT NULL,
  export_crop_area_pct DECIMAL(5, 2),  -- % of cultivated area for export crops
  subsistence_area_pct DECIMAL(5, 2),  -- % for subsistence crops (rice, wheat)
  avg_holding_size_ha DECIMAL(10, 2),  -- Farm size (larger = more commercial)
  export_volume_ratio DECIMAL(5, 2),  -- Export volume / total production
  commercialization_score DECIMAL(5, 2),  -- 0–100 index
  
  UNIQUE(district_id, year)
);

-- Forecasts table (precomputed)
CREATE TABLE forecasts (
  id BIGSERIAL PRIMARY KEY,
  district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
  crop_id INT NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
  forecast_month DATE NOT NULL,  -- Target month
  forecast_yield_kg_ha DECIMAL(10, 2),  -- Predicted yield
  lower_ci_95 DECIMAL(10, 2),  -- 95% confidence lower bound
  upper_ci_95 DECIMAL(10, 2),  -- 95% confidence upper bound
  forecast_model VARCHAR(50),  -- 'ARIMA' | 'ExponentialSmoothing' | 'Prophet'
  rmse_kg_ha DECIMAL(10, 2),  -- Historical validation RMSE
  mae_kg_ha DECIMAL(10, 2),  -- Historical validation MAE
  mape_pct DECIMAL(5, 2),  -- Historical validation MAPE
  forecast_date TIMESTAMPTZ DEFAULT NOW(),  -- When forecast was generated
  
  UNIQUE(district_id, crop_id, forecast_month, forecast_model)
);

-- Indexes for forecasts
CREATE INDEX idx_forecasts_district_month ON forecasts(district_id, forecast_month DESC);
CREATE INDEX idx_forecasts_valid_from ON forecasts(forecast_date DESC);

-- Materialized view for performance
CREATE MATERIALIZED VIEW vw_district_yield_summary AS
SELECT
  d.id as district_id,
  d.name as district_name,
  c.id as crop_id,
  c.name as crop_name,
  AVG(y.yield_kg_ha) as avg_yield_kg_ha,
  MAX(y.yield_kg_ha) as max_yield_kg_ha,
  MIN(y.yield_kg_ha) as min_yield_kg_ha,
  STDDEV(y.yield_kg_ha) as stddev_yield,
  COUNT(y.year) as years_of_data
FROM districts d
JOIN yields y ON d.id = y.district_id
JOIN crops c ON y.crop_id = c.id
WHERE y.year >= 2014
GROUP BY d.id, d.name, c.id, c.name
WITH NO DATA;

-- Refresh weekly after ETL
-- REFRESH MATERIALIZED VIEW CONCURRENTLY vw_district_yield_summary;