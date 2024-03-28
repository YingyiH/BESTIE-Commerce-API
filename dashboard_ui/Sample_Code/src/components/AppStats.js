import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://35.235.112.242:8100/stats`)
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
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Product create</th>
							<th>Product review</th>
						</tr>
						<tr>
							<td># Product number: {stats['num_products']}</td>
							<td># Review number: {stats['num_reviews']}</td>
                            <td># Onsale number: {stats['num_onsale_products']}</td>
						</tr>
						<tr>
							<td colspan="2">Max price: {stats['max_price']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
