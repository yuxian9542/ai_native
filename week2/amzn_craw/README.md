# Amazon Reviews Crawler

A comprehensive Python-based web crawler for extracting Amazon product reviews. This project includes both backend crawling functionality and a web interface for easy interaction.

## Features

- **Search Products**: Search Amazon products by keyword and get top results
- **Extract Reviews**: Parse and extract structured review data from Amazon product pages
- **Multi-page Support**: Crawl multiple pages of reviews with pagination
- **Star Rating Filter**: Filter reviews by specific star ratings (1-5 stars)
- **AJAX Support**: Handle both static HTML and dynamic AJAX review content
- **Web Interface**: Flask-based web application for easy interaction
- **Data Export**: Save results in HTML and JSON formats with logging

## Project Structure

```markdown:week2/amzn_craw/README.md
<code_block_to_apply_changes_from>
week2/amzn_craw/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── amzn_crawl_backend.py       # Core crawling engine
├── web_app.py                  # Flask web application
├── find_api.py                 # API exploration utilities
├── minimize_params.py          # Parameter optimization
├── templates/                  # HTML templates
│   ├── index.html             # Main search interface
│   └── results.html           # Results display page
├── output/                     # Generated results
│   ├── results_*.html         # HTML formatted results
│   └── results_*.log          # Execution logs
└── test.jax                   # Sample AJAX test data
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd week2/amzn_craw
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

**Basic usage** - Search and extract reviews:
```python
from amzn_crawl_backend import amzn_review_main

# Search for "laptop" and get reviews from top 3 products, 2 pages each
results = amzn_review_main("laptop", num_result=3, total_pages=2)

# Filter by star rating (e.g., only 5-star reviews)
results = amzn_review_main("laptop", num_result=3, star=5, total_pages=2)


### Web Interface

1. **Start the web server**:
   ```bash
   python web_app.py
   ```

2. **Access the interface**:
   - Open your browser to `http://localhost:5000`
   - Enter search terms and parameters
   - View results in formatted HTML tables

### Direct Script Execution

Run the backend directly for testing:
```bash
python amzn_crawl_backend.py
```

## Data Structure

Each review is returned as a dictionary with the following fields:

```python
{
    "content": "Review text content with <br/> tags preserved",
    "star": 4,  # Int (1-5)
    "reviewer": "John Doe",  # Reviewer name
    "review_date": "January 15, 2024",  # Review date
    "verified_purchase": "Verified Purchase"  # Purchase verification status
}
```

## Key Functions

### Core Functions

- `amzn_review_main(search_term, num_result, star, total_pages, debug)` - Main crawling function
- `search_prod(search_term, num_result, debug)` - Search products and return ASINs
- `parse_reviews(html, debug)` - Parse reviews from static HTML
- `parse_reviews_ajax(text, debug)` - Parse reviews from AJAX responses
- `extract_reviews_from_jax_file(file_path)` - Extract reviews from saved AJAX files

### Utility Functions

- `perform_request(method, url, ...)` - HTTP request wrapper with logging
- `set_run_log_file(file_path)` - Configure per-run logging
- `_extract_reviews_from_soup(soup)` - BeautifulSoup-based review extraction

## Configuration

### Request Headers and Cookies

The crawler uses realistic browser headers and session cookies defined in:
- `COOKIES` - Session authentication
- `HEADERS_STATIC` - Static page headers  
- `HEADERS_DYNAMIC` - AJAX request headers

### Parameters

- `DATA` - Default form parameters for AJAX requests
- `STAR_MAP` - Mapping between numeric ratings and Amazon's filter strings
- `ASIN_LIST` - Test product identifiers

## Output

### HTML Results
Generated in `output/results_YYYYMMDD_HHMMSS.html`:
- Formatted tables with product information
- Review content with star ratings
- Responsive design for easy viewing

### Log Files
Generated in `output/results_YYYYMMDD_HHMMSS.log`:
- HTTP request/response details
- Parsing statistics
- Error messages and debugging info

## Error Handling

- **Request Failures**: Graceful handling of network errors
- **Parsing Errors**: Fallback mechanisms for malformed HTML
- **Rate Limiting**: Built-in delays and retry logic
- **Logging**: Comprehensive error logging for debugging

## Technical Details

### Review Extraction

The crawler handles multiple review formats:
1. **Static HTML**: Initial page load with embedded reviews
2. **AJAX Responses**: Dynamically loaded review pages
3. **Translated Content**: Support for multi-language reviews

### AJAX Pattern Matching

Uses sophisticated regex patterns to extract JSON payloads:
```python
append_pattern = r'\[\s*"append"\s*,\s*"#cm_cr-review_list"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\]'
```

### Pagination Handling

Automatically detects and follows pagination:
- Parses "Next page" links
- Handles different pagination formats
- Supports both GET and POST requests

## Limitations

- **Rate Limiting**: Amazon may block excessive requests
- **CAPTCHA**: May encounter anti-bot measures
- **Dynamic Content**: Some content requires JavaScript execution
- **Regional Differences**: Designed for Amazon US marketplace

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational purposes only. Please respect Amazon's robots.txt and terms of service.

## Troubleshooting

### Common Issues

1. **No reviews found**: Check if the product ASIN is valid
2. **Request blocked**: Update cookies and headers
3. **Parsing errors**: Verify HTML structure hasn't changed
4. **Empty results**: Enable debug mode for detailed logging

### Debug Mode

Enable detailed logging:
```python
results = amzn_review_main("search_term", debug=True)
```

This provides:
- HTTP request/response details
- HTML parsing step-by-step
- Review extraction statistics
- Error messages with context
```


