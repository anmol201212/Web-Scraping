import csv
import concurrent.futures
import time
from worker import fetch_data
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")
# Function to create a worker task
def create_worker(page):
    print(f'Retrieving page {page}')
    try:
        data = fetch_data(page)
        return (page, data)
    except Exception as e:
        return (page, {'error': str(e)})

# Function to handle worker result and update progress
def handle_worker_result(result, csv_writer):
    if 'error' in result:
        return

    response_data = result
    if not response_data or response_data.get('status') != 1 or not response_data.get('response') or not response_data['response'].get('response') or not isinstance(response_data['response']['response'].get('docs'), list):
        return

    bids = response_data['response']['response']['docs']

    if not bids or not isinstance(bids[0], dict):
        return

    # Extract desired fields from bid objects
    for bid in bids:
        csv_writer.writerow([
            bid['b_bid_number'][0],
            bid['id'],
            bid['b_category_name'][0],
            bid['b_total_quantity'][0],
            bid['ba_official_details_deptName'][0],
            bid['final_start_date_sort'][0],
            bid['final_end_date_sort'][0]
        ])

# Function to process data and save to CSV file
def process_data_and_save_to_csv(pages=3000):
    max_workers = min(20, pages)  # Limit the number of concurrent workers
    retry_limit = 5  # Number of retries for failed pages
    retry_delay = 5  # Delay in seconds between retries

    with open('bids_data.csv', mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        headers = ['Bid Number', 'RA Number', 'Items', 'Quantity', 'Department', 'Start Date', 'End Date']
        csv_writer.writerow(headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            page_status = {page: 0 for page in range(1, pages + 1)}  # Track retries for each page
            future_to_page = {executor.submit(create_worker, page): page for page in range(1, pages + 1)}
            
            while future_to_page:
                done, _ = concurrent.futures.wait(future_to_page, return_when=concurrent.futures.FIRST_COMPLETED)
                
                for future in done:
                    page = future_to_page[future]
                    try:
                        page, result = future.result()
                        if 'error' in result and result['error']:
                            if page_status[page] < retry_limit:
                                print(f"Error retrieving page {page}: {result['error']}. Retrying...")
                                page_status[page] += 1
                                time.sleep(retry_delay)  # Delay before retrying
                                future_to_page[executor.submit(create_worker, page)] = page
                            else:
                                print(f"Failed to retrieve page {page} after {retry_limit} retries. Skipping...")
                                del future_to_page[future]  # Skip further retries for this page
                        else:
                            handle_worker_result(result, csv_writer)
                            del future_to_page[future]
                    except Exception as e:
                        print(f"Error processing page {page}: {e}")

if __name__ == "__main__":
    process_data_and_save_to_csv()
