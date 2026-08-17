import { useState } from "react";
import DashboardView from "./DashboardView";

// ======== HANDLERS =======
// function to send seller to facebook login
function handleFacebookLogin() {
  // get backend url from env or use default localhost
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  // redirect browser to backend facebook auth endpoint
  window.location.href = `${baseUrl}/api/auth/facebook`;
}

// helper function to initialize seller state synchronously
function getInitialSeller() {
  // parse url search parameters if running in browser
  if (typeof window === "undefined") return null;

  const params = new URLSearchParams(window.location.search);
  const authStatus = params.get("auth");
  const token = params.get("token");
  const sellerId = params.get("seller_id");
  const sellerName = params.get("seller_name");
  const fbUserId = params.get("fb_user_id");

  // check if returning from facebook oauth redirect
  if (authStatus === "success" && sellerName) {
    const sellerData = {
      id: sellerId,
      name: decodeURIComponent(sellerName),
      fb_user_id: fbUserId,
    };
    // persist token and seller data in storage
    if (token) {
      localStorage.setItem("meerkat_token", token);
      sessionStorage.setItem("meerkat_token", token);
    }
    localStorage.setItem("meerkat_seller", JSON.stringify(sellerData));
    sessionStorage.setItem("meerkat_seller", JSON.stringify(sellerData));
    // clean url query params
    window.history.replaceState({}, document.title, window.location.pathname);
    return sellerData;
  }

  // check if seller is already cached in browser storage
  const stored =
    localStorage.getItem("meerkat_seller") ||
    sessionStorage.getItem("meerkat_seller");
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      localStorage.removeItem("meerkat_seller");
      sessionStorage.removeItem("meerkat_seller");
    }
  }

  return null;
}

// ======== APP COMPONENT =======
// main user interface router & controller
function App() {
  // set state for active nav section link
  const [activeTab, setActiveTab] = useState("home");
  // set state for logged in seller profile with initial state function
  const [seller, setSeller] = useState(getInitialSeller);

  // function to log seller out of dashboard
  const handleLogout = () => {
    // clear seller state
    setSeller(null);
    // remove token and session from browser storage
    localStorage.removeItem("meerkat_token");
    localStorage.removeItem("meerkat_seller");
    sessionStorage.removeItem("meerkat_token");
    sessionStorage.removeItem("meerkat_seller");
  };


  // if seller is logged in, show dashboard view
  if (seller) {
    return <DashboardView seller={seller} onLogout={handleLogout} />;
  }

  // render landing / login page interface in modern black and white theme
  return (
    <div className="min-h-screen bg-[#09090b] text-[#f4f4f5] font-sans antialiased flex flex-col">
      {/* ======== NAVBAR ======== */}
      {/* top navigation bar header */}
      <header className="sticky top-0 z-50 w-full flex items-center justify-between px-7 py-4 backdrop-blur-md bg-[#09090b]/85 border-b border-[#27272a]">
        {/* left brand logo text */}
        <a
          href="#home"
          className="font-brand text-xl text-white no-underline flex items-center gap-2 select-none tracking-wide"
        >
          MEERKAT
        </a>

        {/* centered top navigation bar */}
        <nav>
          <ul className="flex items-center gap-7 list-none px-6 py-2 rounded-full border border-[#27272a] bg-[#141417]">
            {/* home navigation link */}
            <li>
              <a
                href="#home"
                className={`text-[14px] font-semibold transition-colors duration-200 no-underline ${
                  activeTab === "home"
                    ? "text-white"
                    : "text-[#a1a1aa] hover:text-white"
                }`}
                onClick={() => setActiveTab("home")}
              >
                Home
              </a>
            </li>
            {/* about navigation link */}
            <li>
              <a
                href="#about"
                className={`text-[14px] font-semibold transition-colors duration-200 no-underline ${
                  activeTab === "about"
                    ? "text-white"
                    : "text-[#a1a1aa] hover:text-white"
                }`}
                onClick={() => setActiveTab("about")}
              >
                About
              </a>
            </li>
            {/* docs navigation link */}
            <li>
              <a
                href="#docs"
                className={`text-[14px] font-semibold transition-colors duration-200 no-underline ${
                  activeTab === "docs"
                    ? "text-white"
                    : "text-[#a1a1aa] hover:text-white"
                }`}
                onClick={() => setActiveTab("docs")}
              >
                Docs
              </a>
            </li>
          </ul>
        </nav>

        {/* demo direct preview button */}
        <button
          onClick={() =>
            setSeller({
              id: "demo",
              name: "Fritz (Demo Seller)",
              fb_user_id: "demo_123",
            })
          }
          className="flex items-center gap-2 px-4 py-2 rounded-full border border-[#27272a] bg-[#141417] text-xs font-semibold text-[#a1a1aa] hover:text-white hover:bg-[#202025] transition-all cursor-pointer"
        >
          <span>Demo Dashboard ↗</span>
        </button>
      </header>

      {/* ======== HERO SECTION ======== */}
      {/* main header section with centered MEE KAT title */}
      <section
        id="home"
        className="flex flex-col items-center justify-center px-6 py-16 text-center max-w-4xl mx-auto flex-1"
      >
        {/* display main title with meerkat image standing in for R */}
        <h1
          className="font-brand flex items-center justify-center text-5xl sm:text-7xl md:text-8xl lg:text-9xl mb-6 select-none drop-shadow-md text-white"
          aria-label="Meerkat"
        >
          <span className="tracking-[-0.06em]">MEE</span>
          <img
            src="/images/Meerkat-main.png"
            alt="R"
            className="h-28 sm:h-44 md:h-56 lg:h-72 xl:h-80 w-auto object-contain drop-shadow-2xl animate-float transition-transform duration-300 -mx-2 sm:-mx-4 md:-mx-8 lg:-mx-12"
          />
          <span className="tracking-[-0.06em]">KAT</span>
        </h1>

        {/* display hero subtitle copy */}
        <p className="text-base sm:text-lg md:text-xl max-w-2xl mb-8 leading-relaxed text-[#a1a1aa]">
          Social Commerce Command Center — Unified Facebook & Instagram
          Messaging, Sales Insights, and AI-Driven Growth Strategy for Sellers.
        </p>

        {/* display login button section */}
        <div className="flex flex-col items-center gap-3">
          <button
            className="bg-[#1877f2] text-white border-none rounded-xl px-8 py-4 text-base font-bold cursor-pointer inline-flex items-center gap-3 shadow-lg shadow-[#1877f2]/25 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-[#1877f2]/40 transition-all duration-200"
            onClick={handleFacebookLogin}
          >
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            Login with Facebook for Business
          </button>
          <span className="text-xs text-[#71717a]">
            Connects your Facebook Page and linked Instagram Business account
          </span>
        </div>
      </section>

      {/* ======== ABOUT SECTION ======== */}
      {/* about project features section */}
      <section id="about" className="max-w-5xl mx-auto px-6 py-16 w-full">
        <h2 className="font-brand text-2xl text-center mb-8 text-white">
          About Meerkat
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* feature card 1 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              📥 Unified Inbox
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              Read all customer messages from Facebook Pages and Instagram
              Business in one centralized, read-only dashboard.
            </p>
          </div>
          {/* feature card 2 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              📊 Sales Analytics
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              Track weekly reach, link clicks, profile views, and inquiry volume
              pulling directly from Meta Insights API.
            </p>
          </div>
          {/* feature card 3 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              🤖 AI Sales Strategy (BYOK)
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              Bring your own OpenAI, Anthropic, or Gemini API key to receive
              automated weekly sales growth tips tailored to your shop.
            </p>
          </div>
        </div>
      </section>

      {/* ======== DOCS SECTION ======== */}
      {/* developer documentation and architecture overview */}
      <section id="docs" className="max-w-5xl mx-auto px-6 py-16 w-full">
        <h2 className="font-brand text-2xl text-center mb-8 text-white">
          Documentation & Roadmap
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* doc card 1 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              Phase 1 - 5 (Meta Integration)
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              OAuth authorization, webhook ingestion, token encryption, and
              database storage are fully configured.
            </p>
          </div>
          {/* doc card 2 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              Phase 6 (Unified Inbox UI)
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              Clean black-and-white dashboard view with multi-channel filtering,
              message list, and platform tags.
            </p>
          </div>
          {/* doc card 3 */}
          <div className="rounded-2xl p-7 border border-[#27272a] bg-[#141417] transition-all duration-200 hover:-translate-y-1">
            <h3 className="text-lg font-bold mb-3 text-white">
              Phase 7 - 9 (SSE & AI Strategy)
            </h3>
            <p className="text-sm leading-relaxed text-[#a1a1aa]">
              Real-time Server-Sent Events push for live messages, followed by
              Insights widgets and BYOK AI strategy cards.
            </p>
          </div>
        </div>
      </section>

      {/* ======== FOOTER ======== */}
      {/* page footer credits */}
      <footer className="border-t border-[#27272a] py-8 px-6 text-center text-xs text-[#71717a] mt-auto">
        <p>© 2026 Meerkat App. Social Commerce Command Center.</p>
      </footer>
    </div>
  );
}

export default App;
