# Local Pages Hub

A Python script for automated generation of location-based service pages in WordPress.

## Features

- Bulk page creation from CSV data
- WordPress integration via REST API
- Smart content generation with placeholders (AI-ready)
- Customizable page templates
- CSV data validation
- Detailed logging
- Dry-run mode for testing
- Publication status control

## Requirements

- Python 3.6+
- WordPress site with REST API enabled
- Application password for WordPress authentication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LocalPagesHub.git
cd LocalPagesHub
```

2. Install dependencies:
```bash
pip install requests python-dotenv
```

3. Create `.env` file with your WordPress credentials:
```env
WP_URL=http://your-wordpress-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_app_password
```

## CSV File Format

The script expects a CSV file with the following columns:
- `service` - Service name (e.g., "HVAC Repair")
- `city` - City name (e.g., "Austin")
- `neighborhood` - Neighborhood name (e.g., "Riverside")
- `price_from` - Starting price (e.g., "$99")

Example:
```csv
service,city,neighborhood,price_from
HVAC Repair,Austin,Riverside,$99
AC Installation,Dallas,Uptown,$149
```

## Usage

### Basic Usage
Generate pages from CSV file:
```bash
python generate_local_pages.py data.csv
```

### Advanced Options

1. Publish pages immediately:
```bash
python generate_local_pages.py data.csv --publish
```

2. Test run without creating pages:
```bash
python generate_local_pages.py data.csv --dry-run
```

3. Process limited number of rows:
```bash
python generate_local_pages.py data.csv --limit 5
```

4. Combine options:
```bash
python generate_local_pages.py data.csv --publish --limit 3
```

## Output

### Console Output
The script provides detailed console output for each processed row:
```
Row 1 of 3
Created page: HVAC Repair in Riverside, Austin
Page ID: 123
Slug: /hvac-repair-in-riverside-austin
```

### Log File
All created pages are logged in `output_log.csv`:
```csv
title,slug,status,url,wp_id,notes
HVAC Repair in Riverside...,hvac-repair-in-riverside...,publish,http://...,123,
```

## Page Structure

Each generated page includes:
- Service title (automatically set as H1)
- Featured image
- Service introduction
- Expert services section
- Benefits list
- Service area coverage
- Call to action
- Disclaimer

## Error Handling

The script validates:
- CSV file structure
- Required fields presence
- Empty values
- WordPress API connection
- Duplicate slugs

Error messages are displayed in the console and skipped rows are logged.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 