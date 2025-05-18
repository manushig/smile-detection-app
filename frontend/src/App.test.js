/**
 * Integration & UI Tests for Main App Component.
 *
 * - Mocks backend API, SmileViewer, and SmileDetails for focused logic/UI testing.
 * - Verifies all user interactions and state transitions for the Smile Detection app.
 */

import React from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import App from "./App";

//
// Global mocks and timers for consistency across tests
//
beforeAll(() => {
  jest.useFakeTimers();
  // Mock global URL.createObjectURL to avoid errors in tests (used for Blob image)
  global.URL.createObjectURL = jest.fn(() => "test-object-url");
});
afterAll(() => {
  jest.useRealTimers();
  delete global.URL.createObjectURL;
});

//
// Mock child components to focus on App logic and avoid rendering actual UI
//
jest.mock("./components/SmileViewer", () => (props) => (
  <div data-testid="smile-viewer">{props.imageSrc ? "image" : "no image"}</div>
));
jest.mock("./components/SmileDetails", () => (props) => (
  <div data-testid="smile-details">
    {props.smileDetected ? "smile detected" : "no smile detected"}
  </div>
));

//
// Mock backend API module to control test responses
//
jest.mock("./api/SmileApi", () => ({
  fetchSmileDetection: jest.fn(),
}));
const { fetchSmileDetection } = require("./api/SmileApi");

//
// Test Suite for App Component
//
describe("App", () => {
  // Clear mocks before each test for isolation
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Should render all initial elements and UI text correctly.
  it("renders initial state", () => {
    render(<App />);
    expect(screen.getByText(/smile detection app/i)).toBeInTheDocument();
    expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start/i })).toBeEnabled();
    expect(screen.getByRole("button", { name: /stop/i })).toBeDisabled();
    expect(screen.getByLabelText(/model:/i)).toBeInTheDocument();
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent(/no image/i);
    expect(screen.getByTestId("smile-details")).toHaveTextContent(
      /no smile detected/i
    );
  });

  // Should correctly enable/disable Start and Stop buttons, and update status message accordingly.
  it("start/stop button enables/disables correctly", () => {
    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });
    const stopButton = screen.getByRole("button", { name: /stop/i });

    fireEvent.click(startButton);
    expect(startButton).toBeDisabled();
    expect(stopButton).toBeEnabled();
    expect(screen.getByText(/keep smiling/i)).toBeInTheDocument();

    fireEvent.click(stopButton);
    expect(startButton).toBeEnabled();
    expect(stopButton).toBeDisabled();
    expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument();
  });

  // Should update model selection and reflect change in UI.
  it("changes model selection", () => {
    render(<App />);
    const select = screen.getByLabelText(/model:/i);
    fireEvent.change(select, { target: { value: "dlib" } });
    expect(select.value).toBe("dlib");
  });

  // Should handle a 200 response from backend (smile detected, coords/image present).
  it("handles a successful smile detection (200 response)", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: {
        "x-smile-coords": JSON.stringify([{ x: 1, y: 2, w: 3, h: 4 }]),
      },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    // Simulate polling interval
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    // "image" is rendered, confirming setImageSrc was called and image is present
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent("image");
  });

  // Should handle a 204 response from backend (no smile detected).
  it("handles no smile detected (204 response)", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 204,
      headers: {},
      data: new Blob([], { type: "image/jpeg" }),
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByText(/keep smiling/i)).toBeInTheDocument();
  });

  // Should show error message if API call fails (network error).
  it("handles API/network error", async () => {
    fetchSmileDetection.mockRejectedValue(new Error("Network Error"));

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() =>
      expect(
        screen.getByText(/could not connect to backend/i)
      ).toBeInTheDocument()
    );
  });

  // Should show error message if API returns unhandled status (e.g., 500).
  it("shows error if backend returns unknown status", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 500,
      headers: {},
      data: null,
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() =>
      expect(screen.getByText(/error occurred/i)).toBeInTheDocument()
    );
  });

  // Should handle missing x-smile-coords header gracefully (fallback, no error).
  it("handles missing x-smile-coords header gracefully", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: {}, // No x-smile-coords header
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
  });

  // Should handle single-quoted JSON in x-smile-coords header (inner catch).
  it("parses single-quoted JSON in coordsHeader (inner catch)", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: { "x-smile-coords": "[{'x':1,'y':2,'w':3,'h':4}]" },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
  });

  // Should handle completely invalid coordsHeader (fallback path, no crash).
  it("handles bad coordsHeader: both JSON.parse and fallback", async () => {
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: { "x-smile-coords": "not a json string" },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /start/i }));

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });

    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    // No error thrown, just fallback path for coords
  });
});
