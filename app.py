from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize geolocator
geolocator = Nominatim(user_agent="supply-chain-tracker")

# In-memory database with users and RFID details
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "warehouse": {"password": "warehouse123", "role": "Warehouse"},
    "distributor": {"password": "distributor123", "role": "Distributor"},
    "retailer": {"password": "retailer123", "role": "Retailer"}
}

database = [
    {"id": 1, "rfid": "F62CFF3", "latitude": "00.0000", "longitude": "00.0000", "temperature": "29,10", "humidity": "61.90"},
    {"id": 2, "rfid": "7A2CEA80", "latitude": "13.1718", "longitude": "77.5362", "temperature": "29,10", "humidity": "61.90"},
    {"id": 3, "rfid": "3c4d5e6f", "latitude": "19.0760", "longitude": "72.8777", "temperature": "29,10", "humidity": "61.90"},
    {"id": 4, "rfid": "4d5e6f7g", "latitude": "13.0827", "longitude": "80.2707", "temperature": "29,10", "humidity": "61.90"}
]

# Function to get address from latitude and longitude
def get_address(latitude, longitude):
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        return location.address if location else "Address not found"
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return "Geocoding error"

@app.route('/home')
def home():
    return render_template('home.html')
# Home page route
@app.route('/')
def Search_product():
    return render_template('index.html')

# About us page route
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user["password"] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Display RFID tag details based on user role
    user_role = session['role']
    return render_template('dashboard.html', user_role=user_role, database=database)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Search item by ID or RFID route
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    item = next((item for item in database if str(item["id"]) == search_query or item["rfid"] == search_query), None)

    if item:
        address = get_address(item["latitude"], item["longitude"])
        item["address"] = address
        return render_template('location.html', item=item)
    else:
        return render_template('location.html', item=None, error="Item not found")
    
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Retrieve data from the POST request
        rfid = request.form.get('rfid')
        latitude = request.form.get('lat')
        longitude = request.form.get('lon')
        temperature = request.form.get('temp')
        humidity = request.form.get('hum')

        # Print or process the received data
        print(f"Received data - RFID: {rfid}, Latitude: {latitude}, Longitude: {longitude}, Temperature: {temperature}, Humidity: {humidity}")
        
        existing_item = next((item for item in database if item["rfid"] == rfid), None)

        if existing_item:
            # Update the existing item with new data
            existing_item["latitude"] = latitude
            existing_item["longitude"] = longitude
            existing_item["temperature"] = temperature
            existing_item["humidity"] = humidity
        else:
            print("Invalid RFID tag ")
            user = str(input("want add new tag?"))
            if user == "add new":
                new_item = {
                    "id": len(database) + 1,
                    "rfid": rfid,
                    "latitude": latitude,
                    "longitude": longitude,
                    "temperature": temperature,
                    "humidity": humidity
                }
                database.append(new_item)
            else:
                print("permision to add new RFID card is declined")
            

        # Respond back to ESP8266 with success status
        return jsonify({"status": "success", "message": "Data received successfully"}), 200
        print("OK")
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
