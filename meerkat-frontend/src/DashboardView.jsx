import { useEffect, useState } from "react";

// ======== DASHBOARD VIEW COMPONENT =======
// main dashboard layout view after facebook login
function DashboardView({ seller, onLogout }) {
  // set active navigation tab state
  const [activeNav, setActiveNav] = useState("inbox");
  // set active platform filter state
  const [platformFilter, setPlatformFilter] = useState("all");
  // set search query string state
  const [searchQuery, setSearchQuery] = useState("");
  // set active conversation selection state
  const [selectedChatId, setSelectedChatId] = useState(null);
  // set state for real messages from backend
  const [messagesList, setMessagesList] = useState([]);
  // set loading state for message fetching
  const [isLoading, setIsLoading] = useState(false);

  // base backend url from environment
  const apiBaseUrl =
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  // ======== FETCH MESSAGES FROM BACKEND =======
  // fetch real ingested customer messages from backend endpoint
  useEffect(() => {
    // track whether effect is active to prevent state update on unmounted component
    let isMounted = true;

    // build query url with platform filter
    const url =
      platformFilter === "all"
        ? `${apiBaseUrl}/api/messages`
        : `${apiBaseUrl}/api/messages?platform=${platformFilter}`;

    // retrieve session auth token from browser storage
    const token =
      localStorage.getItem("meerkat_token") ||
      sessionStorage.getItem("meerkat_token");
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    // execute fetch request
    fetch(url, { headers })
      .then((res) => {
        // check if token is invalid or expired
        if (res.status === 401) {
          if (onLogout) onLogout();
          throw new Error("Unauthorized");
        }
        if (!res.ok) throw new Error("Failed to fetch messages");
        return res.json();
      })
      .then((data) => {
        if (!isMounted) return;
        // set messages array
        const fetchedMessages = data.messages || [];
        setMessagesList(fetchedMessages);
        // default select first conversation key if none selected
        if (fetchedMessages.length > 0) {
          const firstKey = `${fetchedMessages[0].platform}_${fetchedMessages[0].sender_id}`;
          setSelectedChatId((prev) => prev || firstKey);
        }
      })
      .catch((err) => {
        console.error("Error fetching messages:", err);
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });


    return () => {
      isMounted = false;
    };
  }, [platformFilter, apiBaseUrl, onLogout]);


  // fallback sample conversations if no real messages exist in database yet
  const fallbackConversations = [
    {
      id: "demo-1",
      sender_id: "demo_user_1",
      platform: "facebook",
      channelName: "Manila Craft Shop",
      time: "10:42 AM",
      snippet: "Hi! Available pa ba itong leather wallet?",
      messages: [
        {
          id: "101",
          text: "Hi! Available pa ba itong leather wallet? Magkano po pag custom initials?",
          time: "10:42 AM",
        },
      ],
    },
    {
      id: "demo-2",
      sender_id: "demo_user_2",
      platform: "instagram",
      channelName: "@manilacrafts",
      time: "9:15 AM",
      snippet: "How much is the shipping fee to Cebu?",
      messages: [
        {
          id: "201",
          text: "How much is the shipping fee to Cebu for 2 sets?",
          time: "9:15 AM",
        },
      ],
    },
    {
      id: "demo-3",
      sender_id: "demo_user_3",
      platform: "facebook",
      channelName: "Manila Craft Shop",
      time: "Yesterday",
      snippet: "Thank you! Received the items safely.",
      messages: [
        {
          id: "301",
          text: "Thank you! Received the items safely. Excellent quality! ⭐⭐⭐⭐⭐",
          time: "Yesterday 4:20 PM",
        },
      ],
    },
  ];

  // ======== GROUP MESSAGES INTO CONVERSATIONS =======
  // group raw messages into unique customer conversation threads
  const conversations = (() => {
    // return fallback demo conversations if no real messages
    if (!messagesList || messagesList.length === 0) {
      return fallbackConversations;
    }

    // map to group messages by conversation key
    const groupMap = new Map();

    // loop through all messages from backend
    messagesList.forEach((msg) => {
      // create conversation key by platform and sender id
      const convKey = `${msg.platform}_${msg.sender_id}`;

      // check if conversation is already in map
      if (!groupMap.has(convKey)) {
        // create new conversation entry
        groupMap.set(convKey, {
          id: convKey,
          sender_id: msg.sender_id,
          sender_name: msg.sender_name,
          sender_profile_pic: msg.sender_profile_pic,
          platform: msg.platform,
          recipient_id: msg.recipient_id,
          created_at: msg.created_at,
          snippet: msg.message_text,
          messages: [],
        });
      } else {
        // update name and profile pic if available on subsequent messages
        const existing = groupMap.get(convKey);
        if (!existing.sender_name && msg.sender_name) {
          existing.sender_name = msg.sender_name;
        }
        if (!existing.sender_profile_pic && msg.sender_profile_pic) {
          existing.sender_profile_pic = msg.sender_profile_pic;
        }
      }

      // add message to conversation thread
      groupMap.get(convKey).messages.push(msg);
    });

    // convert map to array and sort messages inside conversation oldest first
    return Array.from(groupMap.values()).map((conv) => {
      // sort messages chronologically so chat reads top to bottom
      const sortedMessages = [...conv.messages].sort((a, b) => {
        const timeA = new Date(a.created_at || 0).getTime();
        const timeB = new Date(b.created_at || 0).getTime();
        return timeA - timeB;
      });

      return {
        ...conv,
        messages: sortedMessages,
      };
    });
  })();

  // filter conversations by search query string
  const filteredConversations = conversations.filter((chat) => {
    // check search match against sender name, sender id, or message text inside conversation
    const name = chat.sender_name || "";
    const sender = chat.sender_id || "";
    const matchesName = name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSender = sender.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesMessages = (chat.messages || []).some((m) =>
      (m.message_text || m.text || "").toLowerCase().includes(searchQuery.toLowerCase())
    );
    return matchesName || matchesSender || matchesMessages;
  });

  // get currently active selected conversation object
  const activeChat =
    conversations.find((c) => c.id === selectedChatId) || conversations[0];



  // render dashboard interface
  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#09090b] text-[#f4f4f5] font-sans antialiased">
      {/* ======== SIDEBAR ======== */}
      {/* left vertical navigation sidebar */}
      <aside className="w-[260px] shrink-0 border-r border-[#27272a] bg-[#141417] flex flex-col justify-between p-5">
        {/* top section with brand logo and nav menu */}
        <div className="flex flex-col">
          {/* brand logo header */}
          <div className="flex items-center gap-2.5 mb-6 px-2">
            <div className="w-7 h-7 bg-white text-black font-brand rounded-lg flex items-center justify-center text-xs font-normal">
              M
            </div>
            <span className="font-brand text-lg text-white tracking-wide">
              Meerkat
            </span>
          </div>

          {/* navigation menu label */}
          <div className="text-[11px] font-semibold uppercase tracking-wider text-[#71717a] mb-2 px-2">
            Menu
          </div>

          {/* navigation items list */}
          <nav className="flex flex-col gap-1">
            {/* unified inbox tab link */}
            <button
              onClick={() => setActiveNav("inbox")}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 text-left ${
                activeNav === "inbox"
                  ? "bg-white text-black font-semibold"
                  : "text-[#a1a1aa] hover:bg-[#202025] hover:text-[#f4f4f5]"
              }`}
            >
              <span>📥</span> Unified Inbox
            </button>

            {/* sales insights tab link */}
            <button
              onClick={() => setActiveNav("insights")}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 text-left ${
                activeNav === "insights"
                  ? "bg-white text-black font-semibold"
                  : "text-[#a1a1aa] hover:bg-[#202025] hover:text-[#f4f4f5]"
              }`}
            >
              <span>📊</span> Sales Insights
            </button>

            {/* ai strategy tab link */}
            <button
              onClick={() => setActiveNav("strategy")}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 text-left ${
                activeNav === "strategy"
                  ? "bg-white text-black font-semibold"
                  : "text-[#a1a1aa] hover:bg-[#202025] hover:text-[#f4f4f5]"
              }`}
            >
              <span>💡</span> AI Strategy
            </button>

            {/* settings tab link */}
            <button
              onClick={() => setActiveNav("settings")}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 text-left ${
                activeNav === "settings"
                  ? "bg-white text-black font-semibold"
                  : "text-[#a1a1aa] hover:bg-[#202025] hover:text-[#f4f4f5]"
              }`}
            >
              <span>⚙️</span> Settings (BYOK)
            </button>
          </nav>
        </div>

        {/* bottom section with connected channels and user profile */}
        <div className="flex flex-col gap-4">
          {/* connected channels status card */}
          <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-3">
            <div className="flex items-center justify-between text-xs font-semibold text-[#f4f4f5] mb-2">
              <span>Connected Channels</span>
              <span className="flex items-center gap-1.5 text-[11px] font-medium text-[#22c55e]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e]"></span>
                Live
              </span>
            </div>

            {/* facebook page row */}
            <div className="flex items-center gap-2 text-xs py-1 text-[#a1a1aa]">
              <span className="text-[11px] font-bold text-[#1877f2] bg-[#1877f2]/15 border border-[#1877f2]/25 px-1.5 py-0.5 rounded">
                FB
              </span>
              <span className="truncate">Manila Craft Shop</span>
            </div>

            {/* instagram account row */}
            <div className="flex items-center gap-2 text-xs py-1 text-[#a1a1aa]">
              <span className="text-[11px] font-bold text-[#e1306c] bg-[#e1306c]/15 border border-[#e1306c]/25 px-1.5 py-0.5 rounded">
                IG
              </span>
              <span className="truncate">@manilacrafts</span>
            </div>
          </div>

          {/* logged in seller profile block */}
          <div className="flex items-center justify-between pt-3 border-t border-[#27272a]">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-[#202025] border border-[#27272a] flex items-center justify-center text-xs font-semibold text-white">
                {seller?.name ? seller.name.charAt(0).toUpperCase() : "S"}
              </div>
              <div className="flex flex-col">
                <span className="text-[13px] font-semibold text-white truncate max-w-[110px]">
                  {seller?.name || "Fritz (Seller)"}
                </span>
                <span className="text-[11px] text-[#a1a1aa]">Connected to Meta</span>
              </div>
            </div>

            {/* logout button */}
            <button
              onClick={onLogout}
              className="text-[#71717a] hover:text-white text-xs p-1 rounded transition-colors"
              title="Logout"
              aria-label="Logout"
            >
              <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* ======== MAIN CONTENT AREA ======== */}
      {/* center and right dashboard work area */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#09090b]">
        {/* top header toolbar */}
        <header className="h-[65px] px-6 border-b border-[#27272a] bg-[#141417] flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-[17px] font-bold text-white tracking-tight">
              Unified Inbox
            </h1>
            <p className="text-xs text-[#a1a1aa] mt-0.5">
              Phase 6 MVP — Read-only customer messages
            </p>
          </div>

          {/* platform filter pill buttons */}
          <div className="flex items-center gap-3">
            <div className="flex bg-[#18181b] border border-[#27272a] rounded-lg p-1 gap-1">
              <button
                onClick={() => setPlatformFilter("all")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  platformFilter === "all"
                    ? "bg-white text-black font-semibold"
                    : "text-[#a1a1aa] hover:text-[#f4f4f5]"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setPlatformFilter("facebook")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  platformFilter === "facebook"
                    ? "bg-white text-black font-semibold"
                    : "text-[#a1a1aa] hover:text-[#f4f4f5]"
                }`}
              >
                Facebook
              </button>
              <button
                onClick={() => setPlatformFilter("instagram")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  platformFilter === "instagram"
                    ? "bg-white text-black font-semibold"
                    : "text-[#a1a1aa] hover:text-[#f4f4f5]"
                }`}
              >
                Instagram
              </button>
            </div>
          </div>
        </header>

        {/* 3-column split view layout */}
        <div className="flex-1 flex overflow-hidden">
          {/* ======== LEFT: CONVERSATIONS LIST ======== */}
          <div className="w-[340px] shrink-0 border-r border-[#27272a] bg-[#141417] flex flex-col">
            {/* search box */}
            <div className="p-3 border-b border-[#27272a]">
              <input
                type="text"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#18181b] border border-[#27272a] rounded-md px-3 py-2 text-xs text-white placeholder-[#71717a] outline-none focus:border-[#52525b] transition-colors"
              />
            </div>

            {/* conversation items scroll area */}
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="p-6 text-center text-xs text-[#71717a]">
                  Loading messages...
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="p-6 text-center text-xs text-[#71717a]">
                  No messages found
                </div>
              ) : (
                filteredConversations.map((chat) => (
                  <div
                    key={chat.id}
                    onClick={() => setSelectedChatId(chat.id)}
                    className={`p-3.5 border-b border-[#1f1f23] cursor-pointer transition-colors duration-150 flex flex-col gap-1.5 ${
                      selectedChatId === chat.id
                        ? "bg-[#18181b] border-l-2 border-l-white"
                        : "hover:bg-[#202025]"
                    }`}
                  >
                    {/* header row with sender and time */}
                    <div className="flex items-center justify-between">
                      <span className="text-[13px] font-semibold text-white truncate max-w-[170px]">
                        {chat.sender_name || (chat.sender_id ? `User #${chat.sender_id.slice(-6)}` : "Customer")}
                      </span>
                      <span className="text-[11px] text-[#71717a]">
                        {chat.created_at
                          ? new Date(chat.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })
                          : chat.time || "Recent"}
                      </span>
                    </div>

                    {/* snippet text */}
                    <p className="text-xs text-[#a1a1aa] truncate">
                      {chat.snippet || chat.message_text}
                    </p>

                    {/* platform badge */}
                    <div className="flex items-center mt-0.5">
                      {chat.platform === "facebook" ? (
                        <span className="bg-[#1877f2]/15 text-[#60a5fa] border border-[#1877f2]/30 px-1.5 py-0.5 rounded text-[10px] font-semibold">
                          Facebook
                        </span>
                      ) : (
                        <span className="bg-[#e1306c]/15 text-[#f472b6] border border-[#e1306c]/30 px-1.5 py-0.5 rounded text-[10px] font-semibold">
                          Instagram
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* ======== CENTER: CHAT DETAIL VIEW ======== */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#09090b]">
            {/* active conversation top header */}
            <div className="h-[57px] px-5 border-b border-[#27272a] bg-[#141417] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                {activeChat?.sender_profile_pic ? (
                  <img
                    src={activeChat.sender_profile_pic}
                    alt="Avatar"
                    className="w-8 h-8 rounded-full object-cover border border-[#27272a]"
                  />
                ) : (
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                      activeChat?.platform === "facebook"
                        ? "bg-[#1877f2]"
                        : "bg-[#e1306c]"
                    }`}
                  >
                    {activeChat?.sender_name
                      ? activeChat.sender_name.charAt(0).toUpperCase()
                      : activeChat?.sender_id ? activeChat.sender_id.charAt(0).toUpperCase() : "C"}
                  </div>
                )}
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-white">
                    {activeChat?.sender_name || (activeChat?.sender_id ? `User #${activeChat.sender_id}` : "Customer")}
                  </span>
                  <span className="text-[11px] text-[#a1a1aa]">
                    via {activeChat?.platform === "facebook" ? "Facebook Page" : "Instagram"}
                  </span>
                </div>
              </div>
            </div>


            {/* chat message body */}
            <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-3">
              {activeChat?.messages && activeChat.messages.length > 0 ? (
                activeChat.messages.map((msg) => (
                  <div
                    key={msg.id}
                    className="max-w-[75%] p-3.5 rounded-xl text-[13px] leading-relaxed bg-[#141417] border border-[#27272a] text-[#f4f4f5] self-start rounded-bl-sm flex flex-col gap-1"
                  >
                    <span>{msg.message_text || msg.text}</span>
                    <span className="text-[10px] text-[#71717a] self-end">
                      {msg.created_at
                        ? new Date(msg.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : msg.time || ""}
                    </span>
                  </div>
                ))
              ) : activeChat?.message_text ? (
                <div className="max-w-[75%] p-3.5 rounded-xl text-[13px] leading-relaxed bg-[#141417] border border-[#27272a] text-[#f4f4f5] self-start rounded-bl-sm">
                  {activeChat.message_text}
                </div>
              ) : null}

              {/* read-only MVP notice banner */}
              <div className="mt-auto bg-[#f59e0b]/10 border border-dashed border-[#f59e0b]/40 text-[#fbbf24] p-3.5 rounded-lg text-xs text-center leading-relaxed">
                ℹ️ Phase 6 MVP Notice: Dashboard inbox is currently{" "}
                <strong>read-only</strong>. To reply to customer inquiries, please open
                Facebook Business Suite / Meta Inbox.
              </div>
            </div>
          </div>

          {/* ======== RIGHT: WIDGET OVERVIEW PANE ======== */}
          <div className="w-[300px] shrink-0 border-l border-[#27272a] bg-[#141417] p-4 flex flex-col gap-4 overflow-y-auto">
            {/* sales overview widget card */}
            <div className="bg-[#18181b] border border-[#27272a] rounded-lg p-3.5">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[13px] font-semibold text-white">
                  Sales Overview
                </span>
                <span className="text-[10px] text-[#71717a] border border-[#27272a] px-1.5 py-0.5 rounded">
                  Phase 8
                </span>
              </div>

              {/* stat rows */}
              <div className="flex flex-col text-xs">
                <div className="flex justify-between py-1.5 border-b border-[#27272a] text-[#a1a1aa]">
                  <span>Weekly Reach</span>
                  <span className="font-semibold text-white">1,240</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#27272a] text-[#a1a1aa]">
                  <span>Link Clicks</span>
                  <span className="font-semibold text-white">85</span>
                </div>
                <div className="flex justify-between py-1.5 text-[#a1a1aa]">
                  <span>Conversations</span>
                  <span className="font-semibold text-white">{conversations.length || 24}</span>
                </div>
              </div>
            </div>


            {/* ai strategy tip widget card */}
            <div className="bg-gradient-to-b from-[#1f1f23] to-[#141417] border border-[#3f3f46] rounded-lg p-3.5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[13px] font-semibold text-white">
                  AI Strategy Tip
                </span>
                <span className="text-[10px] font-semibold bg-[#a855f7]/15 text-[#c084fc] border border-[#a855f7]/30 px-1.5 py-0.5 rounded">
                  Phase 9
                </span>
              </div>
              <p className="text-xs leading-relaxed text-[#f4f4f5] mt-1">
                "Your Tuesday posts generate 3x more inquiries than weekends.
                Schedule your next leather wallet drop for Tuesday at 7:00 PM!"
              </p>
              <div className="text-[10px] text-[#71717a] mt-2.5">
                Powered by BYOK LLM Key (Gemini / OpenAI)
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardView;
