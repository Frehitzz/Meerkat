import { useEffect, useState } from "react";

// ======== HANDLERS =======
// function to send seller to facebook login
function handleFacebookLogin() {
  // redirect browser to backend facebook auth endpoint
  window.location.href = "http://localhost:8000/api/auth/facebook";
}

// ======== APP COMPONENT =======
// main user interface view
function App() {
  // set state for ping backend status message
  const [message, setMessage] = useState("Loading...");

  // fetch server status on component load
  useEffect(() => {
    // send request to backend ping link
    fetch("http://localhost:8000/api/ping")
      // turn reply into json object
      .then((res) => res.json())
      // update state with backend reply text
      .then((data) => setMessage(data.message))
      // catch network or server errors
      .catch((err) => setMessage("Failed to reach backend: " + err.message));
  }, []);

  // render interface UI
  return (
    <div>
      {/* display main title */}
      <h1>Meerkat</h1>
      {/* display backend ping status */}
      <p>{message}</p>

      {/* display login section */}
      <div>
        {/* display login button for facebook business */}
        <button onClick={handleFacebookLogin}>
          Login with Facebook for Business
        </button>
      </div>
    </div>
  );
}

export default App;
