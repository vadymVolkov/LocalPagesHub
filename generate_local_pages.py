import os
import csv
import re
import argparse
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Create WordPress pages based on CSV file data'
    )
    parser.add_argument(
        'csv_file',
        help='Path to CSV file with data (must contain columns: service, city, neighborhood, price_from)'
    )
    parser.add_argument(
        '--publish',
        action='store_true',
        help='Publish pages immediately instead of saving as drafts'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview pages without creating them in WordPress'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit the number of rows to process',
        default=None
    )
    return parser.parse_args()

# Load environment variables
load_dotenv()

wp_url = os.getenv("WP_URL")
username = os.getenv("WP_USERNAME")
app_password = os.getenv("WP_APP_PASSWORD").replace(" ", "")  # Remove spaces

def get_ai_content(content_type, service, city, neighborhood, price_from):
    """
    Placeholder for AI content generation function.
    
    Parameters:
    content_type - type of content to generate (intro, expertise, coverage, cta)
    service - service name
    city - city name
    neighborhood - neighborhood name
    price_from - starting price
    """
    placeholders = {
        'intro': f"Professional {service} services in {neighborhood}, {city} starting from {price_from}. Our experienced team provides fast and reliable solutions for all your needs.",
        
        'expertise': f"With years of experience serving {city} residents, our {service} experts are your trusted choice in {neighborhood}. We combine local expertise with professional excellence to deliver outstanding results every time.",
        
        'coverage': f"Our service area includes all of {neighborhood} and surrounding {city} neighborhoods. We're strategically located to provide quick response times throughout the entire service area.",
        
        'cta': f"Ready to schedule your {service} service? Contact us now to get started with our professional team in {neighborhood}. Call today for a free consultation!"
    }
    
    return placeholders.get(content_type, "[AI Content Placeholder]")

def get_service_image_url(service, city):
    """
    Placeholder for image generation and upload function.
    In the future, this will handle AI image generation and upload to WordPress media library
    """
    # Temporarily return a fixed URL
    return "http://localpageshub.local/wp-content/uploads/2025/04/images.jpeg"

def create_slug(service, neighborhood, city):
    """Create a slug for the page"""
    # Combine parts in the required format
    raw_slug = f"{service} in {neighborhood} {city}"
    
    # Convert to lowercase
    slug = raw_slug.lower()
    
    # Replace all special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove hyphens from start and end
    slug = slug.strip('-')
    
    return slug

def clean_html_content(content):
    """Clean HTML content before sending to WordPress"""
    # Разбиваем контент на блоки по wp:paragraph или wp:heading
    blocks = content.split('<!-- /wp:')
    cleaned_blocks = []
    
    for block in blocks:
        if not block.strip():
            continue
            
        # Очищаем содержимое блока
        parts = block.split('-->')
        if len(parts) > 1:
            # Первая часть - комментарий wp:block
            wp_comment = parts[0].strip()
            # Остальное - содержимое блока
            block_content = '-->'.join(parts[1:])
            
            # Очищаем содержимое
            cleaned_content = (
                block_content
                .strip()  # Убираем пробелы в начале и конце
                .replace('  ', ' ')  # Заменяем двойные пробелы
                .replace('\n\n\n', '\n\n')  # Убираем тройные переносы строк
            )
            
            # Собираем блок обратно
            cleaned_block = f"{wp_comment}-->{cleaned_content}"
            cleaned_blocks.append(cleaned_block)
    
    # Собираем контент обратно с правильными закрывающими тегами
    result = ''
    for block in cleaned_blocks:
        if block:
            result += f"{block}<!-- /wp:"
            
    return result

def create_page_content(service, city, neighborhood, price_from):
    """Create HTML content for the page"""
    # Get image URL
    image_url = get_service_image_url(service, city)
    
    # Get content from AI (currently placeholders)
    intro = get_ai_content('intro', service, city, neighborhood, price_from)
    expertise = get_ai_content('expertise', service, city, neighborhood, price_from)
    coverage = get_ai_content('coverage', service, city, neighborhood, price_from)
    cta = get_ai_content('cta', service, city, neighborhood, price_from)
    
    content = f"""<!-- wp:image -->
<figure class="wp-block-image">
<img src="{image_url}" alt="{service} services in {city}" />
</figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>{intro}</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Expert {service} Services in {neighborhood}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{expertise}</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Why Choose Our Services</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li>Starting from {price_from}</li>
<li>Licensed and certified professionals</li>
<li>24/7 emergency service availability</li>
<li>Same-day appointments available</li>
<li>Serving {neighborhood} and surrounding areas</li>
<li>100% satisfaction guaranteed</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>Service Area Coverage</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{coverage}</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Schedule Your Service Today</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{cta}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>*Service available in {neighborhood}, {city} and surrounding areas. Prices may vary depending on service requirements.</em></p>
<!-- /wp:paragraph -->"""

    return content.strip()

def create_wp_page(title, content, service, city, neighborhood, price_from, slug, publish=False):
    """Create a page in WordPress"""
    endpoint = f"{wp_url}/wp-json/wp/v2/pages"
    
    payload = {
        "title": title,
        "content": content,
        "status": "publish" if publish else "draft",
        "slug": slug,
        "meta": {
            "service_area": f"{neighborhood}, {city}",
            "service_type": service,
            "price_from": price_from,
            "featured_image_url": get_service_image_url(service, city)
        }
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            auth=HTTPBasicAuth(username, app_password),
            verify=False
        )
        return response
    except requests.exceptions.RequestException as e:
        return None

def validate_csv_file(file_path):
    """Check file existence and structure"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    required_columns = {'service', 'city', 'neighborhood', 'price_from'}
    
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader, None)
        
        if not headers:
            raise ValueError("CSV file is empty")
        
        headers_set = set(map(str.strip, headers))
        missing_columns = required_columns - headers_set
        
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV file: {', '.join(missing_columns)}")

def get_content_preview(content):
    """Get first two lines of content"""
    lines = content.strip().split('\n')
    preview_lines = [line for line in lines if line.strip() and not line.startswith('<!--')][:2]
    return '\n'.join(preview_lines)

def write_to_log(log_data):
    """Write page data to output_log.csv"""
    log_file = "output_log.csv"
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'slug', 'status', 'url', 'wp_id', 'notes'])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(log_data)

def main():
    # Get command line arguments
    args = parse_arguments()
    
    try:
        # Validate CSV file
        validate_csv_file(args.csv_file)
        
        # Read data from CSV
        with open(args.csv_file, 'r') as file:
            lines = list(csv.DictReader(file))
            total_rows = len(lines)
            
            # Apply limit if specified
            if args.limit is not None:
                lines = lines[:args.limit]
                total_rows = min(args.limit, total_rows)
            
            for i, row in enumerate(lines, 1):
                print(f"\nRow {i} of {total_rows}")
                
                try:
                    # Validate row
                    required_fields = {'service', 'city', 'neighborhood', 'price_from'}
                    missing_fields = []
                    
                    for field in required_fields:
                        value = row.get(field, '').strip()
                        if not value:  # Проверяем на пустую строку после strip()
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"⚠️ Skipped row {i}: missing or empty field(s) \"{', '.join(missing_fields)}\"")
                        continue
                    
                    # Process valid row
                    service = row['service'].strip()
                    city = row['city'].strip()
                    neighborhood = row['neighborhood'].strip()
                    price_from = row['price_from'].strip()
                    
                    # Create page title and other data
                    title = f"{service} in {neighborhood}, {city}"
                    original_slug = create_slug(service, neighborhood, city)
                    content = create_page_content(service, city, neighborhood, price_from)
                    
                    if args.dry_run:
                        print("💡 Dry-run: Страница не создана, только предпросмотр")
                        print(f"Title: {title}")
                        print(f"Slug: /{original_slug}")
                        print("\nContent preview:")
                        print(get_content_preview(content))
                        print("\n" + "-"*50)
                    else:
                        # Create WordPress page
                        response = create_wp_page(
                            title, 
                            content, 
                            service, 
                            city, 
                            neighborhood, 
                            price_from, 
                            original_slug,
                            publish=args.publish
                        )
                        
                        if response and response.status_code == 201:
                            data = response.json()
                            print(f"Created page: {title}")
                            print(f"Page ID: {data['id']}")
                            print(f"Slug: /{data['slug']}")
                            
                            # Log the created page
                            notes = f"⚠️ WP changed slug: {original_slug} → {data['slug']}" if data['slug'] != original_slug else ""
                            
                            log_data = {
                                'title': title,
                                'slug': data['slug'],
                                'status': 'publish' if args.publish else 'draft',
                                'url': data['link'],
                                'wp_id': data['id'],
                                'notes': notes
                            }
                            write_to_log(log_data)
                        else:
                            print(f"Error creating page: {title}")
                        
                except Exception as e:
                    print(f"Error processing page: {str(e)}")
                    continue
            
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 