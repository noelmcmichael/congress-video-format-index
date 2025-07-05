# Congress Video Format Index

A comprehensive database and analysis tool for video streaming formats used by US Congress committees and subcommittees.

## Project Overview

This project systematically catalogs the different video streaming formats, platforms, and technical specifications used by committees and subcommittees in the US House of Representatives and US Senate for broadcasting hearings and proceedings.

## Project Structure

```
congress_video_format_index/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── src/                      # Source code
│   ├── __init__.py
│   ├── scrapers/            # Web scraping modules
│   │   ├── __init__.py
│   │   ├── house_scraper.py
│   │   ├── senate_scraper.py
│   │   └── video_analyzer.py
│   ├── database/            # Database models and operations
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── database.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── data/                    # Data storage
│   ├── raw/                 # Raw scraped data
│   ├── processed/           # Cleaned and processed data
│   └── congress_video.db    # SQLite database
├── reports/                 # Generated reports and analysis
└── scripts/                 # Execution scripts
    ├── collect_committees.py
    ├── scrape_hearings.py
    └── analyze_formats.py
```

## Implementation Plan

### Phase 1: Project Setup ✅
- [x] Initialize git repository
- [x] Set up Python virtual environment
- [x] Install required dependencies
- [x] Create project structure
- [x] Document initial README

### Phase 2: Data Collection Strategy ✅
- [x] Identify official sources for committee listings
- [x] Create scrapers for House committee directory
- [x] Create scrapers for Senate committee directory
- [x] Build tools to discover hearing pages

### Phase 3: Database Design ✅
- [x] Design schema for committees, subcommittees, hearings
- [x] Implement SQLite database
- [x] Create data models and relationships

### Phase 4: Web Scraping Implementation ✅
- [x] Build robust web scraping framework
- [x] Handle different website structures
- [x] Implement rate limiting and error handling
- [x] Create video format detection tools

### Phase 5: Video Format Analysis 🔄
- [x] Detect YouTube embeds and specifications
- [x] Identify other streaming platforms
- [x] Extract technical details (resolution, codec, etc.)
- [ ] Handle live vs recorded content differences
- [ ] Improve video format detection accuracy

### Phase 6: Data Organization & Analysis 🔄
- [ ] Create comprehensive reports by committee
- [ ] Generate format usage statistics
- [ ] Build visualization tools
- [ ] Export data in multiple formats

## Target Data Sources

### House of Representatives
- Main committees: https://www.house.gov/committees
- Committee hearing pages and video archives
- Individual committee websites

### Senate
- Main committees: https://www.senate.gov/committees/
- Committee hearing pages and video archives
- Individual committee websites

## Video Formats to Catalog

- **YouTube**: Embedded players, live streams, recorded hearings
- **Custom Players**: Committee-specific streaming solutions
- **Third-party Platforms**: Vimeo, other streaming services
- **Technical Specifications**: Resolution, codec, streaming protocol, accessibility features

## Progress Log

### 2025-01-07
- ✅ Initial project setup complete
- ✅ Git repository initialized
- ✅ Python virtual environment created
- ✅ Dependencies installed
- ✅ Project structure documented

### 2025-01-05 (Major Milestone!)
- ✅ **Successfully scraped 47 Congressional committees** (23 House + 24 Senate)
- ✅ **Discovered 278 committee hearings** (79 House + 199 Senate)
- ✅ **Identified 8 video streaming instances** across different platforms
- ✅ Database schema implemented with full relational structure
- ✅ Robust web scraping framework with rate limiting and error handling
- ✅ Video format detection for YouTube, JWPlayer, and custom platforms
- ✅ GitHub repository created and synchronized

### Current Status
- **Infrastructure**: Complete and operational
- **Data Collection**: Successfully collecting from both chambers
- **Video Detection**: Basic detection working, needs refinement
- **Database**: 47 committees stored with proper metadata

### Next Steps
- Improve video format detection accuracy
- Create comprehensive analysis reports
- Build visualization dashboard
- Export data in multiple formats for research use

## Installation

```bash
# Clone repository
git clone <repository-url>
cd congress_video_format_index

# Set up virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Usage

Coming soon - scripts and tools will be documented as they're developed.

## Contributing

This project follows systematic development practices:
- All changes are committed incrementally
- Progress is documented in README.md
- Code is organized in logical modules
- Comprehensive testing before deployment

## License

TBD