import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
    const [message, setMessage] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get("http://192.168.141.1:8000/");
                setMessage(response.data.message);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, []);

    return (
        <div>
            <h1>FastAPI + React on Wi-Fi Direct</h1>
            <p>{message}</p>
        </div>
    );
};

export default App;
