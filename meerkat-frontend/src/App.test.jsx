import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";
import DashboardView from "./DashboardView";

describe("App Component", () => {
  // ======== TESTS =======
  // test that the app displays the correct title
  it("renders the application title", () => {
    // render the app component
    render(<App />);

    // make sure the main heading is on the screen
    expect(
      screen.getByRole("heading", { name: "Meerkat" }),
    ).toBeInTheDocument();
  });

  // test rendering of facebook login button
  it("renders facebook login button", () => {
    // render the app component
    render(<App />);

    // make sure facebook login button is present on screen
    expect(
      screen.getByRole("button", { name: "Login with Facebook for Business" }),
    ).toBeInTheDocument();
  });

  // test rendering of dashboard view for logged in seller
  it("renders dashboard unified inbox and filters for seller", () => {
    // mock seller profile object
    const mockSeller = {
      id: 1,
      name: "Maria Santos",
      fb_user_id: "123456",
    };

    // render dashboard view
    render(<DashboardView seller={mockSeller} onLogout={() => {}} />);

    // make sure unified inbox heading is present
    expect(
      screen.getByRole("heading", { name: "Unified Inbox" }),
    ).toBeInTheDocument();

    // make sure seller name is displayed
    expect(screen.getByText("Maria Santos")).toBeInTheDocument();

    // make sure platform filter buttons are present
    expect(screen.getByRole("button", { name: "All" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Facebook" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Instagram" })).toBeInTheDocument();
  });
});

