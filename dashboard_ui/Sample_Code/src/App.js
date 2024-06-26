import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import EventLoggerStats from './components/EventLogger';

function App() {

    const endpoints = ["get_products", "get_reviews"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="260px" width="400px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1>Event Logger</h1>
                <EventLoggerStats/>
            </div>
        </div>
    );

}



export default App;
