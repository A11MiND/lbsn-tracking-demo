import axios from 'axios';

// Configuration
const TARGET_URL = "https://api.flytaxiapp.com/v6/gps/get_user_nearby_drivers";
const HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP2A.220505.008)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PHPSESSID=3clulv7sodl7v0t050duag5miu; AWSALB=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ; AWSALBCORS=HxU4n3wk1vr6PjKNKPzEXaAXYvvIW6klxr2j7LsgjcaJLz9lPKrWflE+Ige0/1xNChdv+Djb4XD9EUx/UkvqPIhfXy3zEs92jD7XwiCxNImwlHaFtBZXcFRNrATJ"
};

const BASE_PAYLOAD = {
    "access_token": "RzViMXl2RmFuSlV1TUluRFRBTUFuNjJqNHRoNHQzUjVPc3Rka1lKbGdVYz0",
    "uid": "4342015",
    "ct_list": "1",
    "app_list": "32,33,37",
    "lang": "1",
    "city_id": "1"
};

const STEP_SIZE = 0.02; // Approx 2km

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    const { latStart, latEnd, lonStart, lonEnd } = req.body;

    if (!latStart || !latEnd || !lonStart || !lonEnd) {
        return res.status(400).json({ message: 'Missing coordinates' });
    }

    const driversFound = [];
    const uniqueLocations = new Set();
    const gridPoints = [];

    let currentLat = parseFloat(latStart);
    const endLat = parseFloat(latEnd);
    const startLon = parseFloat(lonStart);
    const endLon = parseFloat(lonEnd);

    // Safety check: Limit the number of iterations to prevent Vercel timeout
    let iterations = 0;
    const MAX_ITERATIONS = 50; 

    // Loop logic: lat decreases (North to South), lon increases (West to East)
    // Ensure loops run correctly regardless of input order
    const latMax = Math.max(currentLat, endLat);
    const latMin = Math.min(currentLat, endLat);
    const lonMin = Math.min(startLon, endLon);
    const lonMax = Math.max(startLon, endLon);

    console.log(`Scanning from Lat: ${latMax} to ${latMin}, Lon: ${lonMin} to ${lonMax}`);

    for (let lat = latMax; lat > latMin; lat -= STEP_SIZE) {
        for (let lon = lonMin; lon < lonMax; lon += STEP_SIZE) {
            if (iterations >= MAX_ITERATIONS) {
                break;
            }
            iterations++;

            gridPoints.push({ lat, lng: lon });

            try {
                const params = new URLSearchParams();
                for (const [key, value] of Object.entries(BASE_PAYLOAD)) {
                    params.append(key, value);
                }
                params.append('lat', lat.toString());
                params.append('lng', lon.toString());

                const response = await axios.post(TARGET_URL, params, { headers: HEADERS });

                if (response.data && response.data.data && response.data.data.driver_list) {
                    const list = response.data.data.driver_list;
                    list.forEach(driver => {
                        const key = `${driver.lat},${driver.lng}`;
                        if (!uniqueLocations.has(key)) {
                            uniqueLocations.add(key);
                            driversFound.push({
                                lat: parseFloat(driver.lat),
                                lng: parseFloat(driver.lng),
                                direction: driver.direction,
                                speed: driver.speed
                            });
                        }
                    });
                }
            } catch (error) {
                console.error(`Error scanning ${lat}, ${lon}:`, error.message);
            }
            
            // Small delay to be polite, but minimal for Vercel speed
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    }

    res.status(200).json({ 
        drivers: driversFound, 
        count: driversFound.length,
        gridPoints: gridPoints,
        message: iterations >= MAX_ITERATIONS ? "Scan limit reached (partial results)" : "Scan complete"
    });
}
