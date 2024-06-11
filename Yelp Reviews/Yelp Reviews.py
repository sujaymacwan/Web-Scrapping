import requests
from bs4 import BeautifulSoup
import csv
import re

def clean_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove special characters, numbers, and extra spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    return text

def scrape_restaurant_info(url):
    # Send a GET request to the provided URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract required information
        restaurant_name_element = soup.find('h1', class_='css-1se8maq')
        total_reviews_element = soup.find('a', class_='css-19v1rkv')

        if not restaurant_name_element or not total_reviews_element:
            print(f"Restaurant name or total reviews not found for {url}.")
            return None

        restaurant_name = restaurant_name_element.text.strip()
        
        # Extract total reviews and remove the opening parenthesis
        total_reviews_text = total_reviews_element.text.strip().split(' ')[0].replace(',', '')
        total_reviews = total_reviews_text.lstrip('(')

        print("Restaurant Name:", restaurant_name)
        print("Total Reviews:", total_reviews)

        reviews = []
        review_list_element = soup.find('ul', class_='list__09f24__ynIEd')

        if review_list_element:
            review_elements = soup.find_all('li', class_='css-1q2nwpv')
            for review_element in review_elements:
                reviewer_name_element = review_element.find('a', class_='css-19v1rkv')
                review_text_element = review_element.find('p', class_='comment__09f24__D0cxf')
                rating_element = review_element.find('div', role='img')

                if not reviewer_name_element or not review_text_element or not rating_element:
                    print("Review information not found for a review.")
                    continue

                reviewer_name = reviewer_name_element.text.strip()
                review_text = review_text_element.text.strip()
                rating = rating_element['aria-label'].split(' ')[0]

                # Clean the review text
                review_text = clean_text(review_text)

                print('Review_text:', review_text)
                print('Reviewer:', reviewer_name)
                print('Rating:', rating)

                reviews.append({
                    'Review_text': review_text,
                    'Reviewer': reviewer_name,
                    'Rating': rating
                })

        return {
            'Name': restaurant_name,
            'Total_Reviews': total_reviews,
            'Reviews': reviews
        }
    else:
        print(f"Failed to retrieve data from {url}. Status Code: {response.status_code}")
        return None

def write_to_csv(data, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Name', 'Total_Reviews', 'Review_text', 'Reviewer', 'Rating']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for restaurant_data in data:
            for review in restaurant_data['Reviews']:
                # Clean the review text before writing to CSV
                review_text = clean_text(review['Review_text'])

                writer.writerow({
                    'Name': restaurant_data['Name'],
                    'Total_Reviews': restaurant_data['Total_Reviews'],
                    'Review_text': review_text,
                    'Reviewer': review['Reviewer'],
                    'Rating': review['Rating']
                })

def main():
    # List of restaurant URLs
    restaurant_urls = [
        "https://www.yelp.ca/biz/pai-northern-thai-kitchen-toronto-5?osq=Restaurants",
        "https://www.yelp.ca/biz/pho-friendly-18-vaughan-2",
        "https://www.yelp.ca/biz/kathmandu-restaurant-toronto-2#atb_alias:AboutThisBizSpecialties",
        "https://www.yelp.ca/biz/eat-bkk-thai-kitchen-and-bar-toronto?page_src=related_bizes",
        "https://www.yelp.ca/biz/soya-mandarin-kitchen-toronto?hrid=c8q803BInyTlOTHHKgaxPw"
        # Add more URLs as needed
    ]

    # Scrape data from each URL
    restaurant_data_list = []
    for url in restaurant_urls:
        restaurant_data = scrape_restaurant_info(url)
        if restaurant_data:
            restaurant_data_list.append(restaurant_data)

    # Check if any scraping was successful before proceeding to write to CSV
    if restaurant_data_list:
        # Write the data to a CSV file
        write_to_csv(restaurant_data_list, 'restaurant_reviews.csv')

if __name__ == "__main__":
    main()
