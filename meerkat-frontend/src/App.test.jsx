import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";

// ======== MOCK SETUP =======
// mock the global fetch function
vi.stubGlobal("fetch", vi.fn());

describe("App Component", () => {
  beforeEach(() => {
    // clear all previous mock calls before each test runs
    vi.clearAllMocks();
  });

  // ======== TESTS =======
  // test that the app displays the correct title and the loading state
  it("renders the application title and displays loading message", async () => {
    // mock fetch to stay loading by returning a promise that does not resolve immediately
    fetch.mockReturnValue(new Promise(() => {}));

    // render the app component
    render(<App />);

    // make sure the main heading is on the screen
    expect(
      screen.getByRole("heading", { name: "Meerkat" }),
    ).toBeInTheDocument();
    // make sure the loading text is on the screen
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  // test that the app displays the message returned from the API
  it("renders message from backend api when fetch is successful", async () => {
    // mock fetch to return a successful json reply
    fetch.mockResolvedValue({
      json: () => Promise.resolve({ message: "pong from FastAPI" }),
    });

    // render the app component
    render(<App />);

    // wait for the message to update on the screen
    await waitFor(() => {
      expect(screen.getByText("pong from FastAPI")).toBeInTheDocument();
    });
  });

  // test that the app displays an error message when fetch fails
  it("renders error message when backend api fetch fails", async () => {
    // mock fetch to fail with an error
    fetch.mockRejectedValue(new Error("Network Error"));

    // render the app component
    render(<App />);

    // wait for the error message to update on the screen
    await waitFor(() => {
      expect(
        screen.getByText("Failed to reach backend: Network Error"),
      ).toBeInTheDocument();
    });
  });

  // test rendering of facebook login button
  it("renders facebook login button", async () => {
    // mock fetch to return a successful json reply
    fetch.mockResolvedValue({
      json: () => Promise.resolve({ message: "pong from FastAPI" }),
    });

    // render the app component
    render(<App />);

    // make sure facebook login button is present on screen
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: "Login with Facebook for Business" }),
      ).toBeInTheDocument();
    });
  });
});
