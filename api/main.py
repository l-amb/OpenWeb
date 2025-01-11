from flask import Flask, request, jsonify, send_file, abort
import os
import json

app = Flask(__name__)

# Directory where website sites (JSON files) will be stored
SITES_DIR = 'sites'
os.makedirs(SITES_DIR, exist_ok=True)

@app.route('/save_site', methods=['POST'])
def save_website_site():
    data = request.get_json()
    
    if data is None or 'domain' not in data:
        return jsonify({'error': 'Invalid site data or missing domain'}), 400
    
    # Generate a filename with domain and TLD (e.g., example.com.json)
    domain = data['domain']
    filename = f"{domain}.json"
    filepath = os.path.join(SITES_DIR, filename)
    
    with open(filepath, 'w') as site_file:
        json.dump(data, site_file)
    
    return jsonify({'message': 'Site saved', 'filename': filename}), 201

@app.route('/get_site/<name_tld>', methods=['GET'])
def get_website_site(name_tld):
    # Full path of the file to retrieve (e.g., example.com.json)
    filename = f"{name_tld}.json"
    filepath = os.path.join(SITES_DIR, filename)
    
    if not os.path.exists(filepath):
        return abort(404, description="Site not found")
    
    return send_file(filepath, mimetype='application/json')

@app.route('/search_domains', methods=['GET'])
def search_domains():
    query = request.args.get('query', '')
    matching_domains = []
    
    # Search through all JSON files in the directory
    for site_filename in os.listdir(SITES_DIR):
        filepath = os.path.join(SITES_DIR, site_filename)
        
        # Extract the domain name without the .json extension
        domain = site_filename.rsplit('.', 1)[0]
        
        # Check if the query is in the domain name
        if query.lower() in domain.lower():
            matching_domains.append(domain)
    
    return jsonify({'query': query, 'matching_domains': matching_domains})

@app.route('/search_by_owner', methods=['GET'])
def search_by_owner():
    owner_value = request.args.get('owner', '')
    matching_domains = []

    # Search through all JSON files in the directory
    for site_filename in os.listdir(SITES_DIR):
        filepath = os.path.join(SITES_DIR, site_filename)

        with open(filepath, 'r') as site_file:
            site_data = json.load(site_file)

            # Check if "Info" exists and has the "owner" key with the desired value
            info = site_data.get('Info', {})
            if info.get('owner', '').lower() == owner_value.lower():
                # Add the domain name without the .json extension to results
                domain = site_filename.rsplit('.', 1)[0]
                matching_domains.append(domain)
    
    return jsonify({'owner': owner_value, 'matching_domains': matching_domains})

@app.route('/delete_site', methods=['POST', 'GET'])
def delete_website_site():
    # Get the 'site' parameter from query string
    site = request.args.get('site', '')
    
    if not site:
        return jsonify({'error': 'Site parameter is missing'}), 400

    # Full path of the file to delete (e.g., example.com.json)
    filename = f"{site}.json"
    filepath = os.path.join(SITES_DIR, filename)
    
    if not os.path.exists(filepath):
        return abort(404, description="Site not found")
    
    os.remove(filepath)
    return jsonify({'message': f'Site {site} deleted successfully.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
