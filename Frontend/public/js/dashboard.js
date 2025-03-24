document.addEventListener("DOMContentLoaded", () => {
    fetchLiveData();
});

// Fetch live disaster risk data from backend
async function fetchLiveData() {
    try {
        const earthquakeResponse = await fetch("http://127.0.0.1:5000/live_earthquake_data");
        const floodResponse = await fetch("http://127.0.0.1:5000/live_flood_data");
        const wildfireResponse = await fetch("http://127.0.0.1:5000/live_wildfire_data");

        const earthquakeData = await earthquakeResponse.json();
        const floodData = await floodResponse.json();
        const wildfireData = await wildfireResponse.json();

        if (earthquakeData && earthquakeData.risk_level) {
            updateRiskLevel("earthquake-risk", earthquakeData.risk_level);
        }

        if (floodData && floodData.risk_level) {
            updateRiskLevel("flood-risk", floodData.risk_level);
        }

        if (wildfireData && wildfireData.risk_level) {
            updateRiskLevel("wildfire-risk", wildfireData.risk_level);
        }

    } catch (error) {
        console.error("⚠️ Error fetching live data:", error);
    }
}

// Function to update risk level text instead of graph
function updateRiskLevel(elementId, riskLevel) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = `Risk Level: ${riskLevel}`;
        element.style.color = riskLevel === "High Risk" ? "red" : 
                              riskLevel === "Medium Risk" ? "orange" : "green";
    }
}
