import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")  # Securely load WeatherAPI key
FALLBACK_IMAGE = "https://via.placeholder.com/800x600?text=No+Image+Available"

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    city = None
    city_image_url = None
    city_image_source = None

    if request.method == 'POST':
        city = request.form.get('city').strip()
        if city:
            # 1️⃣ Fetch weather data
            weather_url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
            try:
                response = requests.get(weather_url)
                response.raise_for_status()
                weather_data = response.json()
            except requests.exceptions.RequestException as e:
                weather_data = {'error': f'An error occurred while fetching weather: {e}'}

            # 2️⃣ Fetch city image and Wikipedia page
            try:
                wiki_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "format": "json",
                    "titles": city,
                    "prop": "pageimages|info",
                    "inprop": "url",
                    "pithumbsize": 400
                }
                r = requests.get(wiki_url, params=params)
                data = r.json()
                pages = data["query"]["pages"]
                page = next(iter(pages.values()))
                
                # Get thumbnail image if available
                city_image_url = page.get("thumbnail", {}).get("source", FALLBACK_IMAGE)
                
                # Get full Wikipedia page link
                city_image_source = page.get("fullurl", f"https://en.wikipedia.org/wiki/{city.replace(' ', '_')}")
            except requests.exceptions.RequestException:
                city_image_url = FALLBACK_IMAGE
                city_image_source = f"https://en.wikipedia.org/wiki/{city.replace(' ', '_')}"

    return render_template(
        'index.html',
        weather_data=weather_data,
        city=city,
        city_image_url=city_image_url,
        city_image_source=city_image_source
    )


@app.route('/suggest')
def suggest():
    query = request.args.get("q", "")
    suggestions = []
    if query:
        url = f"http://api.weatherapi.com/v1/search.json?key={API_KEY}&q={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            suggestions = [f"{item['name']}, {item['country']}" for item in data]
        except Exception:
            pass
    return {"suggestions": suggestions}


if __name__ == '__main__':
    app.run(debug=True)
