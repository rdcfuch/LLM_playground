import httpx
import asyncio

async def get_city_lat_long(city_name):
    # API endpoint
    url = "https://geocode.maps.co/search"
    
    # Parameters for the request
    params = {
        "q": city_name
    }
    
    try:
        # Create an AsyncClient instance
        async with httpx.AsyncClient() as client:
            # Send GET request
            response = await client.get(url, params=params)
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            
            # Check if the response contains results
            if data:
                # Extract the first result (usually the most relevant)
                result = data[0]
                latitude = result.get("lat")
                longitude = result.get("lon")
                
                return latitude, longitude
            else:
                print("No results found for the given query.")
                return None, None
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
city_name = "New York"
lat, lon = asyncio.run(get_city_lat_long(city_name))

if lat and lon:
    print(f"Latitude: {lat}, Longitude: {lon}")
else:
    print("Could not retrieve latitude and longitude.")
