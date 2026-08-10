// ======== TEST SETUP =======
// import react to make it available globally in tests
import React from "react";
// import testing library jest-dom for DOM expectations
import "@testing-library/jest-dom";

// define React globally to fix "React is not defined" error in tests
globalThis.React = React;
