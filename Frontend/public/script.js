// 🌍 Disaster Type Selection
document.getElementById("disasterType").addEventListener("change", function () {
    const disasterType = this.value;

    document.getElementById("earthquakeFields").classList.toggle("hidden", disasterType !== "earthquake");
    document.getElementById("floodFields").classList.toggle("hidden", disasterType !== "flood");
    document.getElementById("wildfireFields").classList.toggle("hidden", disasterType !== "wildfire");
});

// 📌 Form Submission & API Request
document.getElementById("predictionForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const disasterType = document.getElementById("disasterType").value;
    const latitude = document.getElementById("latitude").value;
    const longitude = document.getElementById("longitude").value;

    let apiUrl = "";
    let requestBody = { latitude, longitude };

    if (disasterType === "earthquake") {
        requestBody.depth = document.getElementById("depth").value;
        requestBody.magnitude = document.getElementById("magnitude").value;
        apiUrl = "http://127.0.0.1:5000/predict_earthquake";
    } else if (disasterType === "flood") {
        requestBody.rainfall = document.getElementById("rainfall").value;
        requestBody.riverLevel = document.getElementById("riverLevel").value;
        apiUrl = "http://127.0.0.1:5000/predict_flood";
    } else if (disasterType === "wildfire") {
        requestBody.temperature = document.getElementById("temperature").value;
        requestBody.windSpeed = document.getElementById("windSpeed").value;
        apiUrl = "http://127.0.0.1:5000/predict_wildfire";
    }

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody)
        });

        const result = await response.json();
        console.log("API Response:", result); // ✅ Debugging log

        if (response.ok) {
            const riskLevel = result.risk_level || "Unknown Risk";  // Directly use API risk level
            const locationName = result.location || "Unknown Location";
            console.log("Location received:", locationName); // Debugging

            document.getElementById("result").innerHTML = `
                <h3>Predicted Risk Level</h3>
                <p>📍 <b>Location:</b> ${locationName}</p>
                <p style="font-size: 20px; font-weight: bold; color: ${
                    riskLevel === "High Risk" ? "#F44336" : riskLevel === "Medium Risk" ? "#FFC107" : "#4CAF50"
                };">${riskLevel}</p>
            `;

            updateMap(latitude, longitude, riskLevel);
        } else {
            throw new Error(result.error || "Unknown error");
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById("result").innerHTML = "<p style='color: red;'>Error fetching data. Please try again.</p>";
    }
});

// 🗺 Function to Update Map
let map;
let markerLayer = null;

function updateMap(latitude, longitude, riskLevel) {
    if (!map) {
        map = L.map("map").setView([latitude, longitude], 5);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors"
        }).addTo(map);
    }

    if (markerLayer) {
        map.removeLayer(markerLayer);
    }

    const color = riskLevel === "High Risk" ? "red" : riskLevel === "Medium Risk" ? "orange" : "green";
    markerLayer = L.circleMarker([latitude, longitude], {
        color,
        radius: 8
    }).addTo(map).bindPopup(`<b>Risk Level:</b> ${riskLevel}`).openPopup();
}
