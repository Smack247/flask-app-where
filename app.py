from flask import Flask, render_template, request
from flask_lambda import FlaskLambda
import requests
from bs4 import BeautifulSoup
from geopy.distance import geodesic

app = FlaskLambda(__name__)

def get_user_location():
    response = requests.get('https://www.googleapis.com/geolocation/v1/geolocate?key=YOUR_API_KEY')
    location = response.json()
    return location['location']['lat'], location['location']['lng']

def scrape_events(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    events = []
    for event in soup.select('.event'):
        event_info = {
            'name': event.select_one('.event-name').text,
            'date': event.select_one('.event-date').text,
            'location': event.select_one('.event-location').text,
            'link': event.select_one('.event-link')['href'],
            'lat': float(event.select_one('.event-lat').text),
            'lng': float(event.select_one('.event-lng').text)
        }
        events.append(event_info)
    return events

def filter_events(events, user_location, max_distance_km):
    filtered_events = []
    for event in events:
        event_location = (event['lat'], event['lng'])
        distance = geodesic(user_location, event_location).km
        if distance <= max_distance_km:
            filtered_events.append(event)
    return filtered_events

@app.route('/')
def home():
    user_location = (40.730610, -73.935242)  # Fallback user location (example: New York)
    max_distance_km = 10  # Example: 10 km radius
    events = scrape_events('https://localeventswebsite.com')  # Replace with actual URL
    filtered_events = filter_events(events, user_location, max_distance_km)
    return render_template('index.html', events=filtered_events)

@app.route('/get-location', methods=['POST'])
def get_location():
    user_location = get_user_location()
    max_distance_km = request.form.get('max_distance_km', 10, type=int)
    events = scrape_events('https://localeventswebsite.com')  # Replace with actual URL
    filtered_events = filter_events(events, user_location, max_distance_km)
    return render_template('index.html', events=filtered_events)

if __name__ == '__main__':
    app.run(debug=True)

