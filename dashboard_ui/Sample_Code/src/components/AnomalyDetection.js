import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AnomalyDetectionStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://35.235.112.242:8120/Anomaly`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Anomalies")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
        <h1>Stats</h1>
        <table>
            <tbody>
                <tr>
                    <th>ID</th>
                    <th>EventID</th>
                    <th>TraceID</th>
                    <th>EventType</th>
                    <th>anomaly_type</th>
                    <th>description</th>
                </tr>

            </tbody>
        </table>
    </div>
        )
    }
}