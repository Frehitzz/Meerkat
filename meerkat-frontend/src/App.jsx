import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8000/api/ping")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((err) => setMessage("Failed to reach backend: " + err.message));
  }, []);

  return (
    <div>
      <h1>Meerkat</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;
