import { useState, useCallback } from 'react';
import { GoogleMap, useJsApiLoader, Marker, Rectangle } from '@react-google-maps/api';
import axios from 'axios';

const containerStyle = {
  width: '100%',
  height: '100vh'
};

const center = {
  lat: 22.3193,
  lng: 114.1694
};

const HK_BOUNDS = {
  latStart: 22.40,
  latEnd: 22.20,
  lonStart: 114.10,
  lonEnd: 114.30
};

export default function Home() {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: "AIzaSyBuLw6igtDbLECoBfh7XEnsXGkoXwmK2jU"
  });

  const [map, setMap] = useState(null);
  const [drivers, setDrivers] = useState([]);
  const [gridPoints, setGridPoints] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [scanArea, setScanArea] = useState(HK_BOUNDS);
  const [status, setStatus] = useState("");

  const onLoad = useCallback(function callback(map) {
    setMap(map);
  }, []);

  const onUnmount = useCallback(function callback(map) {
    setMap(null);
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setStatus("Scanning area... this may take a moment.");
    setDrivers([]);
    setGridPoints([]);

    try {
      const response = await axios.post('/api/scan', scanArea);
      setDrivers(response.data.drivers);
      setGridPoints(response.data.gridPoints);
      setStatus(`Scan complete! Found ${response.data.count} drivers. ${response.data.message}`);
    } catch (error) {
      console.error(error);
      setStatus("Error during scan. Check console.");
    } finally {
      setScanning(false);
    }
  };

  return isLoaded ? (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar Controls */}
      <div style={{ width: '350px', padding: '20px', background: '#f8f9fa', borderRight: '1px solid #ddd', overflowY: 'auto' }}>
        <h1 style={{ fontSize: '24px', marginBottom: '20px' }}>🚕 FlyTaxi Tracker</h1>
        
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>Scan Area (Lat/Lon)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div>
              <label style={{ fontSize: '12px' }}>Lat Start (North)</label>
              <input 
                type="number" 
                step="0.01"
                value={scanArea.latStart} 
                onChange={(e) => setScanArea({...scanArea, latStart: e.target.value})}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px' }}>Lat End (South)</label>
              <input 
                type="number" 
                step="0.01"
                value={scanArea.latEnd} 
                onChange={(e) => setScanArea({...scanArea, latEnd: e.target.value})}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px' }}>Lon Start (West)</label>
              <input 
                type="number" 
                step="0.01"
                value={scanArea.lonStart} 
                onChange={(e) => setScanArea({...scanArea, lonStart: e.target.value})}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px' }}>Lon End (East)</label>
              <input 
                type="number" 
                step="0.01"
                value={scanArea.lonEnd} 
                onChange={(e) => setScanArea({...scanArea, lonEnd: e.target.value})}
                style={{ width: '100%', padding: '5px' }}
              />
            </div>
          </div>
        </div>

        <button 
          onClick={handleScan} 
          disabled={scanning}
          style={{
            width: '100%',
            padding: '10px',
            background: scanning ? '#ccc' : '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: scanning ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {scanning ? 'Scanning...' : 'Start Scan'}
        </button>

        <div style={{ marginTop: '20px', padding: '10px', background: 'white', borderRadius: '5px', border: '1px solid #eee' }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>Status:</p>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>{status}</p>
        </div>

        {drivers.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <h3>Drivers Found: {drivers.length}</h3>
            <ul style={{ listStyle: 'none', padding: 0, fontSize: '12px', maxHeight: '300px', overflowY: 'auto' }}>
              {drivers.map((d, i) => (
                <li key={i} style={{ padding: '5px', borderBottom: '1px solid #eee' }}>
                  🚕 {d.lat.toFixed(4)}, {d.lng.toFixed(4)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Map */}
      <div style={{ flex: 1 }}>
        <GoogleMap
          mapContainerStyle={containerStyle}
          center={center}
          zoom={12}
          onLoad={onLoad}
          onUnmount={onUnmount}
        >
          {/* Draw Grid Points (Where we scanned) */}
          {gridPoints.map((pt, i) => (
             <Rectangle
                key={`grid-${i}`}
                bounds={{
                    north: pt.lat + 0.01,
                    south: pt.lat - 0.01,
                    east: pt.lng + 0.01,
                    west: pt.lng - 0.01
                }}
                options={{
                    strokeColor: "#FF0000",
                    strokeOpacity: 0.1,
                    strokeWeight: 1,
                    fillColor: "#FF0000",
                    fillOpacity: 0.05
                }}
             />
          ))}

          {/* Draw Drivers */}
          {drivers.map((driver, i) => (
            <Marker
              key={i}
              position={{ lat: driver.lat, lng: driver.lng }}
              label="🚕"
              title={`Speed: ${driver.speed}`}
            />
          ))}
        </GoogleMap>
      </div>
    </div>
  ) : <div>Loading Map...</div>
}
