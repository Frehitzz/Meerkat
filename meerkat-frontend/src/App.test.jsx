import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

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
});
