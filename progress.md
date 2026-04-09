# Project Progress

## Current Status
- Total: 8 features
- Passing: 3 / 8 (37.5%)
- Current: Feature #3 completed, next is Feature #6 (design patent images)

## Session Log
### Session 1 - 2026-03-25 Data Collection & Planning
- Completed: all raw data downloaded and moved to T7
- Completed: technical architecture design
- Blocker: T7 is exFAT, PostgreSQL requires Unix filesystem
- Decision: pause until local disk expanded, then use local SSD for PostgreSQL

### Session 2 - (between sessions) Schema & Trademark ETL
- Completed: Feature #1 - PostgreSQL schema deployed locally
- Completed: Feature #2 - Trademark ETL, 13,998,975 trademarks from 90 zips

### Session 3 - 2026-04-10 Patent ETL
- Completed: Feature #3 - Patent File Wrapper JSON ETL
- Data: 12,774,314 patents (683,022 design, 10,487,754 utility, 25,242 plant)
- Child tables: 35.8M inventors, 7.5M applicants, 499M events, 18.2M publications
- Optimizations applied:
  - Moved raw data from T7 to local SSD (IO bottleneck fix)
  - Skip-resume for already-processed records
  - Drop indexes during bulk load, rebuild after (13.5GB → 273MB during load)
  - skip_delete + ON CONFLICT DO NOTHING for new records
  - Final speed: ~600 records/sec/worker × 6 workers
- Next: Phase 2 - download design patent images for CLIP

## Data Inventory
### PostgreSQL (local SSD: /opt/homebrew/var/postgresql@17/)
- trademarks: 13,998,975 records + classes/owners/statements/design_codes
- patents: 12,774,314 records + inventors/applicants/events/publications
- Database size: ~54 GB

### Raw Data (local copy: raw/patents-fw/)
- 3 zips (58 GB) - patent File Wrapper JSON (can delete after verification)

### Raw Data (T7: /Volumes/T7/uspto-data/)
- raw/trademarks/: 90 zips, ~11.4 GB
- raw/patents-fw/: 3 zips, ~58 GB (original copy)

## Next Steps
1. Feature #6: Download ~683K design patent images → CLIP embeddings → Milvus
2. Feature #4: Data validation report
3. Feature #7: FastAPI risk scoring API
4. Feature #8: ERP integration
