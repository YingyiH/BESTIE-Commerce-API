import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EventLoggerStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://35.235.112.242:8120/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
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
            <thead>
                <tr>
                    <th>Stat ID</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
                {Object.keys(stats).map(statID => (
                    <tr key={statID}>
                        <td>{statID}</td>
                        <td>{stats[statID]}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
        )
    }
}