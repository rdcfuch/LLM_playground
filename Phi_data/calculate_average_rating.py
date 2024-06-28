import pandas as pd

# Load the data
url = 'https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv'
df = pd.read_csv(url)

# Calculate the average rating
average_rating = df['Rating'].mean()

# Print the result
print(f'The average rating of movies is: {average_rating}')