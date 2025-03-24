const express = require("express");
const path = require("path");
const cors = require("cors");

const app = express();
const PORT = 3000; // Frontend runs on port 3000

// Enable CORS (Allows communication with the Flask backend)
app.use(cors());
app.use(express.json());

// Serve static frontend files from "public" folder
app.use(express.static(path.join(__dirname, "public")));

// Handle API requests to fetch predictions from Flask backend
app.post("/predict", async (req, res) => {
    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(req.body),
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.statusText}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error("Error fetching prediction:", error);
        res.status(500).json({ error: "Failed to fetch prediction" });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`🌍 Frontend running at: http://localhost:${PORT}`);
});
