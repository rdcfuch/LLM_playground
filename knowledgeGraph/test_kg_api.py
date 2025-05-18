import requests
import os
import json

# API endpoint
BASE_URL = "http://localhost:8000"

def test_generate_graph():
    # Test data
    test_text = """

The CMBS Security MSBAM 2017-C34, rated by S&P, is a diversified commercial mortgage-backed security supported by a variety of loans across multiple metropolitan regions. One of the key components is a $25.3M loan on 444 West Ocean Blvd, Long Beach, originated by JPMorgan, and secured by a property leased to Premier Business Centers. The asset, located in Los Angeles, CA, has been affected by macroeconomic events such as tariffs and international trade risk. Another critical loan in the pool is a $30M loan on 888 East Ocean, Short Beach, originated by Wells Fargo, tied to a property occupied by Premier Industry Centers and located in San Francisco, CA.

Additional support for the security includes a $15.7M loan on 101 Market Street, originated by CitiBank, secured by a mixed-use property in downtown Oakland, CA. This asset, leased to Bluewave Financial Group and FlexStart Co-Working, has recently seen fluctuations due to local regulatory shifts and commercial zoning reform. Another $42M loan on 707 Mission Street, originated by Bank of America, is backed by a tech campus in San Jose, leased primarily to InnovateX Labs and BitCore Systems. The area has experienced strong demand but is also exposed to macro risks such as interest rate volatility and talent migration.

A $19.5M loan on 3200 Wilshire Blvd in Koreatown, Los Angeles, originated by Morgan Stanley, supports a retail-commercial complex leased to K-Fashion World and Urban Fresh Foods. This asset has seen exposure to consumer spending trends and shifting retail behaviors. Finally, the $23M loan on 500 2nd Avenue in Seattle, WA, originated by Goldman Sachs, is backed by a logistics facility occupied by Pacific Northwest Freight Co., located in an industrial corridor experiencing rising land costs due to zoning changes and port congestion."""
    # Prepare the request
    endpoint = f"{BASE_URL}/generate-graph/"
    payload = {"text": test_text}
    
    try:
        # Send POST request
        response = requests.post(endpoint, json=payload)
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            print("✅ API request successful!")
            print("Generated files:")
            print(f"- Cypher file: {result['cypher_file']}")
            print(f"- HTML visualization: {result['html_visualization']}")
            
            # Verify files exist
            if os.path.exists(result['cypher_file']):
                print("✅ Cypher file generated successfully")
            else:
                print("❌ Cypher file not found")
                
            if os.path.exists(result['html_visualization']):
                print("✅ HTML visualization generated successfully")
            else:
                print("❌ HTML visualization not found")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the API server is running")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    print("Testing Knowledge Graph API...\n")
    test_generate_graph()