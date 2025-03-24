const API_KEY = "5610732233684fb88881c7450c47e451"; // Replace with your actual key

// Initialize map
const map = L.map("map").setView([20.5937, 78.9629], 5); // Default: India

// Load OpenStreetMap tiles
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
}).addTo(map);

// Function to fetch live earthquake data from backend
async function fetchLiveEarthquakeData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/live_data");
        const data = await response.json();

        if (data && data.earthquakes) {
            data.earthquakes.forEach((quake) => {
                const { latitude, longitude, magnitude, risk_level, location } = quake;

                // Set marker color based on risk level
                let markerColor = "green";
                if (risk_level === 1) markerColor = "orange";
                if (risk_level === 2) markerColor = "red";

                // Add earthquake marker
                L.circleMarker([latitude, longitude], {
                    color: markerColor,
                    radius: magnitude * 2,
                    fillOpacity: 0.7,
                })
                    .addTo(map)
                    .bindPopup(
                        `<b>Location:</b> ${location}<br>
                         <b>Magnitude:</b> ${magnitude}<br>
                         <b>Risk Level:</b> ${risk_level === 2 ? "High" : risk_level === 1 ? "Medium" : "Low"}`
                    );
            });
        }
    } catch (error) {
        console.error("⚠️ Error fetching earthquake data:", error);
    }
}

// Fetch data when page loads
fetchLiveEarthquakeData();
