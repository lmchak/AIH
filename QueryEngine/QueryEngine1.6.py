from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_coordinates_from_address(address):
    # Make a request to onemap.gov.sg to get coordinates
    onemap_url = f'https://www.onemap.gov.sg/api/common/elastic/search?searchVal={address}&returnGeom=Y&getAddrDetails=Y&pageNum=1'
    onemap_response = requests.get(onemap_url)
    
    # Print the request and response for debugging
    print(f"get_coordinates_from_address - Request URL: {onemap_url}")
    print(f"get_coordinates_from_address - Response: {onemap_response.status_code} {onemap_response.text}")
    
    # Check if the request was successful
    if onemap_response.status_code == 200:
        # Parse the response JSON
        onemap_data = onemap_response.json()
        
        # Check if any results were found
        if onemap_data['found'] > 0:
            # Extract coordinates from the first result
            coordinates = {
                'latitude': onemap_data['results'][0]['LATITUDE'],
                'longitude': onemap_data['results'][0]['LONGITUDE'],
                'onemap_response': onemap_data  # Add onemap response
            }
            return coordinates
    return None



def get_land_use_from_coordinates(latitude, longitude):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # Make a request to maps.ura.gov.sg to get land use information
    ura_url = f'https://maps.ura.gov.sg/arcgis/rest/services/MP19/Landuse_gaz/MapServer/46/query'
    params = {
        'returnGeometry': 'true',
        'where': '1=1',
        'outSR': '4326',
        'outFields': '*',
        'inSr': '4326',
        'geometry': f'{{"x":{longitude},"y":{latitude},"spatialReference":{{"wkid":4326}}}}',
        'geometryType': 'esriGeometryPoint',
        'spatialRel': 'esriSpatialRelWithin',
        'f': 'json',
    }
    
    # Print the request for debugging
    print(f"get_land_use_from_coordinates - Request URL: {ura_url}")
    
    ura_response = requests.get(ura_url, headers=headers, params=params)
    
    # Print the response for debugging
    print(f"get_land_use_from_coordinates - Response: {ura_response.status_code} {ura_response.text}")
    
    # Check if the request was successful
    if ura_response.status_code == 200:
        # Parse the response JSON
        ura_data = ura_response.json()
        
    # Include coordinates, onemap response, ura response, and road buffer in the result
    result = {
        'coordinates': {'latitude': latitude, 'longitude': longitude},
        'onemap_response': get_coordinates_from_address(latitude),  # Fix here by passing only the address
        'ura_response': ura_data
    }

    # Check if onemap_response is not None before accessing 'results'
    onemap_response = result['onemap_response']
    if onemap_response and 'results' in onemap_response:
        # Call get_road_buffer with ROAD_NAME from onemap_response
        road_name = onemap_response['results'][0].get('ROAD_NAME')
        if road_name:
            road_buffer = get_road_buffer(road_name)
            result['road_buffer'] = road_buffer

    return result




def calculate_buffers(road_cat, landuse, gpr, isCentralArea, isNewtonOrchardRV):
    buffers = {}

    if road_cat == 'CAT1':
        buffers = {
            'Residential Below 6 Storeys': '24m',
            'Residential Above 6 Storeys': '30m',
            'Residential Green': '5m',
            'Residential All': '',
            'Educational Below 6 Storeys': '24m',
            'Educational Above 6 Storeys': '30m',
            'Educational Green': '5m',
            'Educational All': '',
            'Others All': '15m',
            'Others Green': '5m'
        }
    elif road_cat == 'CAT2':
        buffers = {
            'Residential Below 6 Storeys': '12m',
            'Residential Above 6 Storeys': '15m',
            'Residential Green': '5m',
            'Residential All': '',
            'Educational Below 6 Storeys': '12m',
            'Educational Above 6 Storeys': '15m',
            'Educational Green': '5m',
            'Educational All': '',
            'Others All': '7.5m',
            'Others Green': '3m'
        }
    elif road_cat == 'CAT3':
        buffers = {
            'Residential Below 6 Storeys': '7.5m',
            'Residential Above 6 Storeys': '10m',
            'Residential Green': '3m',
            'Residential All': '',
            'Educational Below 6 Storeys': '7.5m',
            'Educational Above 6 Storeys': '10m',
            'Educational Green': '3m',
            'Educational All': '',
            'Others All': '5m',
            'Others Green': '3m'
        }
    elif road_cat == 'CAT4':
        buffers = {
            'Residential Below 6 Storeys': '',
            'Residential Above 6 Storeys': '',
            'Residential Green': '3m',
            'Residential All': '7.5m',
            'Educational Below 6 Storeys': '',
            'Educational Above 6 Storeys': '',
            'Educational Green': '3m',
            'Educational All': '7.5m',
            'Others All': '5m',
            'Others Green': '3m'
        }
    elif road_cat == 'CAT5':
        if landuse == 'Residential DENTIAL' and gpr == 'LND':
            buffers['Residential Green'] = '0m'
        else:
            buffers['Residential Green'] = '3m'
        buffers.update({
            'Residential Below 6 Storeys': '',
            'Residential Above 6 Storeys': '',
            'Residential All': '7.5m',
            'Educational Below 6 Storeys': '',
            'Educational Above 6 Storeys': '',
            'Educational Green': '3m',
            'Educational All': '7.5m',
            'Others All': '5m',
            'Others Green': '3m'
        })
    elif road_cat == 'NCAT':
        if not isCentralArea or isNewtonOrchardRV:
            buffers.update({
                'Residential Green': '3m',
                'Residential All': '7.5m'
            })
        else:
            buffers.update({
                'Residential Green': '',
                'Residential All': 'Subject to detailed evaluation'
            })
        if isCentralArea:
            buffers.update({
                'Educational All': 'Subject to detailed evaluation',
                'Educational Green': ''
            })
        else:
            buffers.update({
                'Educational All': '7.5m',
                'Educational Green': '3m'
            })
        if isCentralArea:
            buffers.update({
                'Others All': 'Subject to detailed evaluation',
                'Others Green': ''
            })
        else:
            buffers.update({
                'Others All': '5m',
                'Others Green': '3m'
            })

    return buffers

def get_road_buffer(road_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    road_cat_url = 'https://maps.ura.gov.sg/ArcGis/rest/services/dcg/LTA_Road_Cat3/MapServer/1/query'
    params = {
        'returnGeometry': 'true',
        'where': f'UPPER(ROAD_NAME) = \'{road_name.upper()}\'',
        'outSR': '4326',
        'outFields': 'ROAD_NAME,ROAD_CAT',
        'f': 'json',
    }

    print(f"get_road_buffer - Request URL: {road_cat_url}")
    road_cat_response = requests.get(road_cat_url, headers=headers, params=params)
    print(f"get_road_buffer - Response: {road_cat_response.status_code} {road_cat_response.text}")

    if road_cat_response.status_code == 200:
        road_cat_data = road_cat_response.json()
        if road_cat_data['features']:
            road_cat = road_cat_data['features'][0]['attributes']['ROAD_CAT']
            buffers = calculate_buffers(road_cat, None, None, False, False)
            return {'road_cat': road_cat, 'road_name': road_name, 'buffers': buffers}
        else:
            return {'error': 'Road not found in the URA database'}, 404
    else:
        return {'error': 'Failed to retrieve road category information'}, 500


@app.route('/get_land_use', methods=['POST'])
def get_land_use():
    # Get the address from the request
    data = request.get_json()
    address = data.get('address')
    
    # Get coordinates from onemap.gov.sg
    coordinates = get_coordinates_from_address(address)
    
    if coordinates:
        onemap_response = coordinates['onemap_response']
        road_name = onemap_response['results'][0].get('ROAD_NAME') if onemap_response and 'results' in onemap_response else None

        # Get land use information from maps.ura.gov.sg
        land_use_data = get_land_use_from_coordinates(coordinates['latitude'], coordinates['longitude'])
        
        if land_use_data:
            features = land_use_data.get('features', [])
            
            # Include coordinates, onemap response, ura response, and road buffer in the result
            result = {
                #'features': features,
                #'coordinates': coordinates,
                'onemap_response': onemap_response,
                'ura_response': land_use_data['ura_response'],
                'road_buffer': get_road_buffer(road_name) if road_name else None
            }
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to retrieve land use information'}), 500
    else:
        return jsonify({'error': 'Failed to retrieve coordinates from address'}), 500



@app.route('/get_road_buffer', methods=['POST'])
def get_road_buffer_route():
    data = request.get_json()
    road_name = data.get('road_name')

    if road_name:
        result = get_road_buffer(road_name)
        return jsonify(result)
    else:
        return jsonify({'error': 'Road name not provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
