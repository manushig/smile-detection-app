/**
 * Integration & UI Tests for Main App Component.
 *
 * - Covers all user flows for smile detection, start/stop logic, and API interactions.
 * - Mocks backend API and child components for focus on App logic and status transitions.
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

async function flushPromises() {
  return await act(async () => {
    // Flush timers
    jest.runOnlyPendingTimers();
    // Allow all useEffect microtasks to run
    await Promise.resolve();
  });
}

//
// Mock timers and URL for Blob URLs used in SmileViewer
//
let blobCounter = 0;
beforeAll(() => {
  jest.useFakeTimers();
  global.URL.createObjectURL = jest.fn(
    () => `test-object-url-${blobCounter++}`
  );
  global.URL.revokeObjectURL = jest.fn();
});
afterAll(() => {
  jest.useRealTimers();
  delete global.URL.createObjectURL;
  delete global.URL.revokeObjectURL;
});

//
// Mock child components (SmileViewer, SmileDetails) to avoid their UI complexity.
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
// Mock the backend API functions
//
jest.mock("./api/SmileApi", () => ({
  startCamera: jest.fn(),
  stopCamera: jest.fn(),
  fetchSmileDetection: jest.fn(),
}));

const {
  startCamera,
  stopCamera,
  fetchSmileDetection,
} = require("./api/SmileApi");

describe("App", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    URL.revokeObjectURL.mockClear();
    blobCounter = 0;
  });

  /**
   * Should render all main UI elements in the initial state.
   */
  it("renders initial state", () => {
    render(<App />);
    expect(screen.getByText(/smile detection app/i)).toBeInTheDocument();
    expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start/i })).toBeEnabled();
    expect(screen.getByRole("button", { name: /stop/i })).toBeDisabled();
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent(/no image/i);
    expect(screen.getByTestId("smile-details")).toHaveTextContent(
      /no smile detected/i
    );
  });

  /**
   * Should call startCamera and begin polling on Start.
   * Should update UI messages and button states accordingly.
   */
  it("starts detection on Start and shows 'Keep smiling!' after camera starts", async () => {
    startCamera.mockResolvedValue();
    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });
    const stopButton = screen.getByRole("button", { name: /stop/i });

    await act(async () => {
      fireEvent.click(startButton);
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await waitFor(() => expect(startButton).toBeDisabled());
    await waitFor(() => expect(stopButton).toBeEnabled());
    expect(screen.getByText(/keep smiling/i)).toBeInTheDocument();
  });

  /**
   * Should handle failure to start camera and display error message.
   */
  it("shows error message if camera fails to start", async () => {
    startCamera.mockRejectedValue(new Error("fail"));
    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });

    await act(async () => {
      fireEvent.click(startButton);
    });
    await waitFor(() =>
      expect(screen.getByText(/failed to start camera/i)).toBeInTheDocument()
    );
    expect(startButton).toBeEnabled();
  });

  /**
   * Should call stopCamera, stop polling, and reset UI on Stop.
   */
  it("stops detection and camera on Stop", async () => {
    startCamera.mockResolvedValue();
    stopCamera.mockResolvedValue();

    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });
    const stopButton = screen.getByRole("button", { name: /stop/i });

    // Start
    await act(async () => {
      fireEvent.click(startButton);
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await waitFor(() => expect(stopButton).toBeEnabled());

    // Stop
    await act(async () => {
      fireEvent.click(stopButton);
    });
    await waitFor(() => expect(stopCamera).toHaveBeenCalled());
    await waitFor(() => expect(startButton).toBeEnabled());
    expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument();
  });

  /**
   * Should handle successful smile detection (200 OK, with coords/image).
   */
  it("polls and handles a 200 response (smile detected)", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: {
        "x-smile-coords": JSON.stringify([{ x: 1, y: 2, w: 3, h: 4 }]),
      },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());

    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByText(/keep smiling/i)).toBeInTheDocument();
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent("image");
  });

  /**
   * Should handle 204 response (no smile detected, but polling is running).
   */
  it("handles 204 response (no smile detected)", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 204,
      headers: {},
      data: new Blob([], { type: "image/jpeg" }),
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByText(/keep smiling/i)).toBeInTheDocument();
  });

  /**
   * Should show a message if backend returns 409 (camera not started).
   */
  it("handles 409 response (camera not started)", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 409,
      headers: {},
      data: null,
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByText(/camera not started/i)).toBeInTheDocument();
  });

  /**
   * Should show a generic error message on backend error (e.g., 500).
   */
  it("handles 500 response (backend error)", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 500,
      headers: {},
      data: null,
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByText(/error occurred/i)).toBeInTheDocument();
  });

  /**
   * Should show a network error if backend cannot be reached.
   */
  it("handles API/network error", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockRejectedValue(new Error("fail"));

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() =>
      expect(
        screen.getByText(/could not connect to backend/i)
      ).toBeInTheDocument()
    );
  });

  /**
   * Should handle stopCamera failure gracefully (no crash, UI still resets).
   */
  it("handles stopCamera failure gracefully", async () => {
    startCamera.mockResolvedValue();
    stopCamera.mockRejectedValue(new Error("Could not stop"));

    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });
    const stopButton = screen.getByRole("button", { name: /stop/i });

    await act(async () => {
      fireEvent.click(startButton);
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await waitFor(() => expect(stopButton).toBeEnabled());

    await act(async () => {
      fireEvent.click(stopButton);
    });
    await waitFor(() => expect(stopCamera).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument()
    );
  });

  /**
   * Should parse coords header that uses single quotes (inner fallback).
   */
  it("handles single-quoted coords header", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: { "x-smile-coords": "[{'x':1,'y':2,'w':3,'h':4}]" },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent("image");
  });

  /**
   * Should handle invalid coords header (invalid JSON, fallback to raw string).
   */
  it("handles invalid coords header (not JSON)", async () => {
    startCamera.mockResolvedValue();
    fetchSmileDetection.mockResolvedValue({
      status: 200,
      headers: { "x-smile-coords": "not a json string" },
      data: new Blob(["img"], { type: "image/jpeg" }),
    });

    render(<App />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /start/i }));
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await act(async () => {
      jest.advanceTimersByTime(1000);
    });
    await waitFor(() => expect(fetchSmileDetection).toHaveBeenCalled());
    expect(screen.getByTestId("smile-viewer")).toHaveTextContent("image");
  });

  /**
   * Should handle stopCamera failure and still update UI.
   */
  it("covers error branch in handleStop if stopCamera fails", async () => {
    startCamera.mockResolvedValue();
    stopCamera.mockRejectedValue(new Error("fail"));

    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });
    const stopButton = screen.getByRole("button", { name: /stop/i });

    await act(async () => {
      fireEvent.click(startButton);
    });
    await waitFor(() => expect(startCamera).toHaveBeenCalled());
    await waitFor(() => expect(stopButton).toBeEnabled());

    await act(async () => {
      fireEvent.click(stopButton);
    });
    await waitFor(() => expect(stopCamera).toHaveBeenCalled());
    await waitFor(() =>
      expect(screen.getByText(/click 'start' to begin/i)).toBeInTheDocument()
    );
  });

  /**
   * Should show spinner overlay while starting camera and hide it after success.
   */
  it("shows spinner overlay while starting camera and hides it after success", async () => {
    // Simulate delayed camera start to show spinner
    let resolveStart;
    startCamera.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveStart = resolve;
        })
    );

    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });

    // Click Start and check for spinner overlay
    act(() => {
      fireEvent.click(startButton);
    });
    expect(document.querySelector(".spinner-overlay")).toBeInTheDocument();

    // Resolve startCamera to finish loading
    await act(async () => {
      resolveStart();
    });

    expect(document.querySelector(".spinner-overlay")).not.toBeInTheDocument();
  });

  /**
   * Should hide spinner overlay if camera fails to start.
   */
  it("hides spinner overlay if camera fails to start", async () => {
    startCamera.mockRejectedValue(new Error("fail"));

    render(<App />);
    const startButton = screen.getByRole("button", { name: /start/i });

    await act(async () => {
      fireEvent.click(startButton);
    });

    expect(document.querySelector(".spinner-overlay")).not.toBeInTheDocument();
  });
});
