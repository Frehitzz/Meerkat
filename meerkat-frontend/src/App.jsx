import { useEffect, useState } from "react";

// ======== HANDLERS =======
// function to send seller to facebook login
function handleFacebookLogin() {
  // get backend url from env or use default localhost
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  // redirect browser to backend facebook auth endpoint
  window.location.href = `${baseUrl}/api/auth/facebook`;
}

// ======== APP COMPONENT =======
// main user interface view
function App() {

  // set state for active nav section link
  const [activeTab, setActiveTab] = useState("home");
  // set state for dark or light theme mode
  const [theme, setTheme] = useState("dark");



  // update document root theme attribute on theme change
  useEffect(() => {
    // apply dark class to root document element when in dark mode
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  // function to toggle theme mode state
  const toggleTheme = () => {
    // switch state between dark and light
    setTheme((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  };

  // render interface UI
  return (
    <div
      className={`min-h-screen transition-colors duration-300 font-sans ${
        theme === "dark"
          ? "bg-[#1A1513] text-[#FAEFDD]"
          : "bg-[#FAF7F2] text-[#2A211D]"
      }`}
    >
      {/* ======== NAVBAR ======== */}
      {/* top navigation bar header */}
      <header
        className={`sticky top-0 z-50 w-full flex items-center justify-between px-7 py-3.5 backdrop-blur-md border-b transition-colors duration-300 ${
          theme === "dark"
            ? "bg-[#1A1513]/85 border-[#453D3C]"
            : "bg-[#FAF7F2]/85 border-[#E5DCD3]"
        }`}
      >
        {/* left brand logo text */}
        <a
          href="#home"
          className="font-brand text-xl text-[#FBB653] no-underline flex items-center gap-2 select-none"
        >
          MEERKAT
        </a>

        {/* centered top navigation bar */}
        <nav>
          <ul
            className={`flex items-center gap-7 list-none px-6 py-2 rounded-full border transition-colors duration-300 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            {/* home navigation link */}
            <li>
              <a
                href="#home"
                className={`text-[14px] font-semibold transition-colors duration-200 no-underline ${
                  activeTab === "home"
                    ? "text-[#FBB653]"
                    : theme === "dark"
                    ? "text-[#D1B69F] hover:text-[#FBB653]"
                    : "text-[#6E5F57] hover:text-[#D4791B]"
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
                    ? "text-[#FBB653]"
                    : theme === "dark"
                    ? "text-[#D1B69F] hover:text-[#FBB653]"
                    : "text-[#6E5F57] hover:text-[#D4791B]"
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
                    ? "text-[#FBB653]"
                    : theme === "dark"
                    ? "text-[#D1B69F] hover:text-[#FBB653]"
                    : "text-[#6E5F57] hover:text-[#D4791B]"
                }`}
                onClick={() => setActiveTab("docs")}
              >
                Docs
              </a>
            </li>
          </ul>
        </nav>

        {/* right light mode dark mode toggle button */}
        <button
          className={`flex items-center gap-2 px-4 py-2 rounded-full border text-[13px] font-semibold cursor-pointer transition-all duration-200 hover:scale-105 ${
            theme === "dark"
              ? "bg-[#2F2A29] border-[#453D3C] text-[#FAEFDD] hover:bg-[#453D3C]"
              : "bg-white border-[#E5DCD3] text-[#2A211D] hover:bg-[#F2EBE1]"
          }`}
          onClick={toggleTheme}
          aria-label="Toggle theme mode"
        >
          <span>{theme === "dark" ? "🌙 Dark" : "☀️ Light"}</span>
        </button>
      </header>

      {/* ======== HERO SECTION ======== */}
      {/* main header section with centered MEE KAT title */}
      <section id="home" className="flex flex-col items-center justify-center px-6 py-16 text-center">
        {/* display main title with meerkat image standing in for R */}
        <h1
          className="font-brand flex items-center justify-center text-5xl sm:text-7xl md:text-8xl lg:text-9xl mb-6 select-none drop-shadow-md"
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
        <p
          className={`text-base sm:text-lg md:text-xl max-w-2xl mb-8 leading-relaxed ${
            theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
          }`}
        >
          Social Commerce Command Center — Unified Facebook & Instagram Messaging,
          Sales Insights, and AI-Driven Growth Strategy for Sellers.
        </p>



        {/* display login button section */}
        <div>
          <button
            className="bg-[#1877f2] text-white border-none rounded-xl px-8 py-4 text-base font-bold cursor-pointer inline-flex items-center gap-3 shadow-lg shadow-[#1877f2]/35 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-[#1877f2]/45 transition-all duration-200"
            onClick={handleFacebookLogin}
          >
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
            Login with Facebook for Business
          </button>
        </div>
      </section>

      {/* ======== ABOUT SECTION ======== */}
      {/* about project features section */}
      <section id="about" className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="font-brand text-3xl text-center mb-8 text-[#FBB653]">
          About Meerkat
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* feature card 1 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              📥 Unified Inbox
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              Read all customer messages from Facebook Pages and Instagram Business
              in one centralized, read-only dashboard.
            </p>
          </div>
          {/* feature card 2 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              📊 Sales Analytics
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              Track weekly reach, link clicks, profile views, and inquiry volume
              pulling directly from Meta Insights API.
            </p>
          </div>
          {/* feature card 3 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              🤖 AI Sales Strategy (BYOK)
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              Bring your own OpenAI, Anthropic, or Gemini API key to receive automated
              weekly sales growth tips tailored to your shop.
            </p>
          </div>
        </div>
      </section>

      {/* ======== DOCS SECTION ======== */}
      {/* developer documentation and architecture overview */}
      <section id="docs" className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="font-brand text-3xl text-center mb-8 text-[#FBB653]">
          Documentation & Roadmap
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* doc card 1 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              Phase 1 - 5 (Meta Integration)
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              OAuth authorization, webhook ingestion, token encryption, and database
              storage are fully configured and deployed on Render.
            </p>
          </div>
          {/* doc card 2 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              Phase 6 (Unified Inbox UI)
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              Building the React dashboard component with filtering, message lists,
              and live platform tags (FB vs IG).
            </p>
          </div>
          {/* doc card 3 */}
          <div
            className={`rounded-2xl p-7 border transition-all duration-200 hover:-translate-y-1 ${
              theme === "dark"
                ? "bg-[#2F2A29] border-[#453D3C]"
                : "bg-white border-[#E5DCD3]"
            }`}
          >
            <h3
              className={`text-lg font-bold mb-3 ${
                theme === "dark" ? "text-[#FAEFDD]" : "text-[#2A211D]"
              }`}
            >
              Phase 7 - 9 (SSE & AI Strategy)
            </h3>
            <p
              className={`text-sm leading-relaxed ${
                theme === "dark" ? "text-[#D1B69F]" : "text-[#6E5F57]"
              }`}
            >
              Real-time Server-Sent Events push for live messages, followed by
              Insights widgets and BYOK AI strategy cards.
            </p>
          </div>
        </div>
      </section>

      {/* ======== FOOTER ======== */}
      {/* page footer credits */}
      <footer
        className={`border-t py-8 px-6 text-center text-xs transition-colors duration-300 ${
          theme === "dark"
            ? "border-[#453D3C] text-[#D1B69F]"
            : "border-[#E5DCD3] text-[#6E5F57]"
        }`}
      >
        <p>© 2026 Meerkat App. Social Commerce Command Center.</p>
      </footer>
    </div>
  );
}

export default App;
