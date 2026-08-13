# Meerkat — Visual UI Design System & Knowledge Base

This document is the visual design specification for **Meerkat**. It contains **live visual previews** of typography, colors, and components so that developers, stakeholders, and AI agents can visually inspect the exact design language.

> 💡 **Tip for viewing:** View this file in VS Code Markdown Preview (`Ctrl+Shift+V` or `Cmd+Shift+V`) or any browser/GitHub markdown renderer to see the live colored swatches, font sizes, and component cards.

---

## 1. Visual Color Swatches & Palette

### Canvas & Surface Layers

<div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px;">

  <!-- base background -->
  <div style="background-color: #0f172a; border: 1px solid #334155; padding: 14px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 32px; height: 32px; background-color: #0f172a; border: 1px solid #334155; border-radius: 6px;"></div>
      <div>
        <strong style="color: #f8fafc; font-size: 14px;">Base Canvas Background</strong>
        <div style="color: #94a3b8; font-size: 12px;">Main workspace canvas background behind cards</div>
      </div>
    </div>
    <code style="background-color: #1e293b; color: #3b82f6; padding: 4px 8px; border-radius: 4px; font-weight: bold;">#0F172A</code>
  </div>

  <!-- sidebar background -->
  <div style="background-color: #0b1120; border: 1px solid #334155; padding: 14px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 32px; height: 32px; background-color: #0b1120; border: 1px solid #334155; border-radius: 6px;"></div>
      <div>
        <strong style="color: #f8fafc; font-size: 14px;">Sidebar Surface</strong>
        <div style="color: #94a3b8; font-size: 12px;">Left navigation panel background</div>
      </div>
    </div>
    <code style="background-color: #1e293b; color: #3b82f6; padding: 4px 8px; border-radius: 4px; font-weight: bold;">#0B1120</code>
  </div>

  <!-- primary card surface -->
  <div style="background-color: #1e293b; border: 1px solid #334155; padding: 14px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 32px; height: 32px; background-color: #1e293b; border: 1px solid #334155; border-radius: 6px;"></div>
      <div>
        <strong style="color: #f8fafc; font-size: 14px;">Primary Card Surface</strong>
        <div style="color: #94a3b8; font-size: 12px;">Default module cards, chat panels, containers</div>
      </div>
    </div>
    <code style="background-color: #0f172a; color: #3b82f6; padding: 4px 8px; border-radius: 4px; font-weight: bold;">#1E293B</code>
  </div>

  <!-- hover surface -->
  <div style="background-color: #334155; border: 1px solid #475569; padding: 14px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 12px;">
      <div style="width: 32px; height: 32px; background-color: #334155; border: 1px solid #475569; border-radius: 6px;"></div>
      <div>
        <strong style="color: #f8fafc; font-size: 14px;">Hover & Selection Surface</strong>
        <div style="color: #94a3b8; font-size: 12px;">Active navigation link, item hover background</div>
      </div>
    </div>
    <code style="background-color: #0f172a; color: #3b82f6; padding: 4px 8px; border-radius: 4px; font-weight: bold;">#334155</code>
  </div>

</div>

### Brand & Platform Accent Colors

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 24px;">

  <!-- meerkat blue -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #3b82f6; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Primary Brand</div>
    <strong style="color: #3b82f6; font-size: 16px; display: block; margin: 4px 0;">Meerkat Blue</strong>
    <code style="font-size: 12px; color: #94a3b8;">#3B82F6</code>
  </div>

  <!-- facebook blue -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #1877f2; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Meta Channel</div>
    <strong style="color: #1877f2; font-size: 16px; display: block; margin: 4px 0;">Facebook Blue</strong>
    <code style="font-size: 12px; color: #94a3b8;">#1877F2</code>
  </div>

  <!-- instagram pink -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #e1306c; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Meta Channel</div>
    <strong style="color: #e1306c; font-size: 16px; display: block; margin: 4px 0;">Instagram Pink</strong>
    <code style="font-size: 12px; color: #94a3b8;">#E1306C</code>
  </div>

  <!-- ai strategy purple -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #8b5cf6; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">AI Strategy</div>
    <strong style="color: #c084fc; font-size: 16px; display: block; margin: 4px 0;">AI Purple</strong>
    <code style="font-size: 12px; color: #94a3b8;">#8B5CF6 / #C084FC</code>
  </div>

  <!-- success green -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #22c55e; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Status</div>
    <strong style="color: #22c55e; font-size: 16px; display: block; margin: 4px 0;">Connected / Live</strong>
    <code style="font-size: 12px; color: #94a3b8;">#22C55E</code>
  </div>

  <!-- warning amber -->
  <div style="background-color: #1e293b; border: 1px solid #334155; border-top: 4px solid #f59e0b; padding: 14px; border-radius: 8px;">
    <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">Notice Banner</div>
    <strong style="color: #f59e0b; font-size: 16px; display: block; margin: 4px 0;">Read-Only Amber</strong>
    <code style="font-size: 12px; color: #94a3b8;">#F59E0B</code>
  </div>

</div>

---

## 2. Visual Typography System (Live Font Previews)

Below are the exact rendered typography styles used across Meerkat's interface.

<!-- 1. Display Hero -->
<div style="background-color: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">1. Display / Hero Title • 40px • Bold (700)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 40px; font-weight: 700; line-height: 1.2; color: #f8fafc; letter-spacing: -0.02em;">
    Social Commerce Command Center
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 8px;">Used for: Main Login Landing Page Main Headline</div>
</div>

<!-- 2. Page Title H1/H2 -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">2. Page / Modal Title (H2) • 24px • Bold (700)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; line-height: 1.3; color: #f8fafc; letter-spacing: -0.01em;">
    Seller Account Login & Settings
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Page headers, dialog titles, onboarding steps</div>
</div>

<!-- 3. Section Header H3 -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">3. Section Header (H3) • 18px • Bold (700)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 700; line-height: 1.4; color: #f8fafc;">
    Unified Message Inbox
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Workspace top bars, main content section titles</div>
</div>

<!-- 4. Card Header H4 -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">4. Card Header / Sender Name (H4) • 14px • SemiBold (600)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; line-height: 1.4; color: #f8fafc;">
    Maria Santos (Manila Craft Shop)
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Conversation sender titles, widget titles, subheadings</div>
</div>

<!-- 5. Body Standard -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">5. Body Standard • 14px • Regular (400)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 400; line-height: 1.5; color: #f8fafc;">
    Hi! Available pa ba itong leather wallet? Magkano po customized initials feature?
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Chat bubble text, standard paragraph body copy</div>
</div>

<!-- 6. Body Small / Muted -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">6. Body Small / Muted • 12px • Regular (400)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 400; line-height: 1.4; color: #94a3b8;">
    Read all customer DMs from Facebook Pages & Instagram Business in one unified inbox.
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Message list previews, feature descriptions, input helper text</div>
</div>

<!-- 7. Tiny Badge / Timestamp -->
<div style="background-color: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; margin-bottom: 6px;">7. Tiny / Timestamp / Badge • 11px • SemiBold (600)</div>
  <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600; line-height: 1.2; color: #94a3b8; letter-spacing: 0.02em;">
    OCT 24, 2026 • 10:42 AM
  </div>
  <div style="font-size: 12px; color: #64748b; margin-top: 6px;">Used for: Conversation list timestamps, badge counters, status tags</div>
</div>

---

## 3. Rendered Component Design Mockups

### A. Facebook Login Action Button

<div style="background-color: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 24px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Component: OAuth Login Button</div>
  
  <button style="background-color: #1877f2; color: #ffffff; border: none; border-radius: 8px; padding: 14px 24px; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 12px; box-shadow: 0 4px 12px rgba(24, 119, 242, 0.3);">
    <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
    Login with Facebook for Business
  </button>
</div>

### B. Platform Channel Badges

<div style="background-color: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 24px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Component: Channel Distinction Badges</div>

  <div style="display: flex; gap: 12px; align-items: center;">
    <!-- facebook tag -->
    <span style="background-color: rgba(24, 119, 242, 0.15); color: #60a5fa; padding: 4px 10px; border-radius: 4px; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600; border: 1px solid rgba(24, 119, 242, 0.3);">
      Facebook Page
    </span>

    <!-- instagram tag -->
    <span style="background-color: rgba(225, 48, 108, 0.15); color: #f472b6; padding: 4px 10px; border-radius: 4px; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600; border: 1px solid rgba(225, 48, 108, 0.3);">
      Instagram Business
    </span>
  </div>
</div>

### C. Conversation List Item Row (Active State)

<div style="background-color: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 24px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Component: Selected Message Row in Inbox</div>

  <div style="background-color: #334155; border-left: 3px solid #3b82f6; padding: 14px; border-radius: 0 6px 6px 0; max-width: 380px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <strong style="color: #f8fafc; font-size: 13px;">Maria Santos</strong>
      <span style="color: #94a3b8; font-size: 11px;">10:42 AM</span>
    </div>
    <div style="color: #94a3b8; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 8px;">
      Hi! Available pa ba itong leather wallet?
    </div>
    <span style="background-color: rgba(24, 119, 242, 0.15); color: #60a5fa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">
      Facebook
    </span>
  </div>
</div>

### D. Read-Only Notice Banner (Phase 6 MVP Rule)

<div style="background-color: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 24px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Component: Phase 6 Read-Only Banner</div>

  <div style="background-color: rgba(245, 158, 11, 0.1); border: 1px dashed #f59e0b; color: #f59e0b; padding: 12px 16px; border-radius: 6px; font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.5; text-align: center;">
    ℹ️ Phase 6 MVP Notice: Dashboard inbox is currently <strong>read-only</strong>. To reply to customer inquiries, please open Facebook Business Suite / Meta Inbox.
  </div>
</div>

### E. AI Strategy Card (Phase 9 Preview)

<div style="background-color: #0f172a; padding: 24px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 24px;">
  <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Component: AI Sales Strategy Card</div>

  <div style="background: linear-gradient(180deg, rgba(139, 92, 246, 0.08) 0%, rgba(30, 41, 59, 1) 100%); border: 1px solid rgba(139, 92, 246, 0.4); padding: 16px; border-radius: 8px; max-width: 320px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <strong style="color: #c084fc; font-size: 13px;">AI Strategy Tip</strong>
      <span style="background-color: rgba(139, 92, 246, 0.2); color: #c084fc; padding: 2px 6px; border-radius: 999px; font-size: 10px; font-weight: 600;">Phase 9</span>
    </div>
    <p style="color: #e2e8f0; font-size: 12px; line-height: 1.5; margin: 0 0 10px 0;">
      "Your Tuesday posts generate 3x more inquiries than weekends. Schedule your next leather wallet drop for Tuesday at 7:00 PM!"
    </p>
    <div style="font-size: 10px; color: #94a3b8;">
      Powered by BYOK LLM Key (Gemini / OpenAI)
    </div>
  </div>
</div>

---

## 4. Developer Quick Reference Token Map

| UI Element | CSS Variable Token | HEX / HSL Value |
|---|---|---|
| Main Page Canvas | `var(--color-bg-base)` | `#0F172A` |
| Sidebar Background | `var(--color-bg-sidebar)` | `#0B1120` |
| Standard Card | `var(--color-surface-card)` | `#1E293B` |
| Card / Nav Hover | `var(--color-surface-hover)` | `#334155` |
| Main Text | `var(--color-text-main)` | `#F8FAFC` |
| Muted Labels / Dates | `var(--color-text-muted)` | `#94A3B8` |
| Primary Blue | `var(--color-primary)` | `#3B82F6` |
| Facebook Accent | `var(--color-fb-brand)` | `#1877F2` |
| Instagram Accent | `var(--color-ig-brand)` | `#E1306C` |
| AI Purple | `var(--color-ai-purple)` | `#8B5CF6` |
