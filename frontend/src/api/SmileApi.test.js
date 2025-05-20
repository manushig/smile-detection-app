/**
 * Smile detection API client tests.
 *
 * - Covers all functions and error branches in SmileApi.js.
 * - Mocks axios for reliable and isolated testing.
 * - Provides professional docstrings and line comments.
 */

import axios from "axios";
import {
  startCamera,
  stopCamera,
  fetchSmileDetection,
  validateSmileStatus,
} from "./SmileApi";

// Mock axios globally for this test suite
jest.mock("axios");

//
// Tests for startCamera
//
describe("startCamera", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Should call /start_camera and return data on success.
   */
  it("calls /start_camera and returns backend data", async () => {
    const mockData = { ok: true };
    axios.post.mockResolvedValue({ data: mockData });

    const result = await startCamera();

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining("/start_camera")
    );
    expect(result).toBe(mockData);
  });

  /**
   * Should propagate backend/network errors for UI to handle.
   */
  it("throws on network/backend error", async () => {
    axios.post.mockRejectedValue(new Error("fail"));

    await expect(startCamera()).rejects.toThrow("fail");
  });
});

//
// Tests for stopCamera
//
describe("stopCamera", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Should call /stop_camera and return data on success.
   */
  it("calls /stop_camera and returns backend data", async () => {
    const mockData = { stopped: true };
    axios.post.mockResolvedValue({ data: mockData });

    const result = await stopCamera();

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining("/stop_camera")
    );
    expect(result).toBe(mockData);
  });

  /**
   * Should propagate backend/network errors for UI to handle.
   */
  it("throws on network/backend error", async () => {
    axios.post.mockRejectedValue(new Error("fail"));

    await expect(stopCamera()).rejects.toThrow("fail");
  });
});

//
// Tests for validateSmileStatus utility
//
describe("validateSmileStatus", () => {
  /**
   * Should return true for valid status codes.
   */
  it("returns true for 200, 204, 500", () => {
    expect(validateSmileStatus(200)).toBe(true);
    expect(validateSmileStatus(204)).toBe(true);
    expect(validateSmileStatus(500)).toBe(true);
  });

  /**
   * Should return false for unexpected codes.
   */
  it("returns false for other status codes", () => {
    expect(validateSmileStatus(404)).toBe(false);
    expect(validateSmileStatus(400)).toBe(false);
    expect(validateSmileStatus(201)).toBe(false);
  });
});

//
// Tests for fetchSmileDetection integration logic
//
describe("fetchSmileDetection", () => {
  // Reset axios mocks after each test for isolation
  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Should call /detect_smile and return response on success.
   */
  it("calls /detect_smile and returns response", async () => {
    const mockResponse = { status: 200, data: "blob" };
    axios.get.mockResolvedValue(mockResponse);

    const result = await fetchSmileDetection();

    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("/detect_smile"),
      expect.objectContaining({
        responseType: "blob",
        validateStatus: expect.any(Function),
      })
    );
    expect(result).toBe(mockResponse);
  });

  /**
   * Should propagate errors thrown by axios (network/backend error).
   */
  it("throws on network/backend error", async () => {
    axios.get.mockRejectedValue(new Error("Network Error"));

    await expect(fetchSmileDetection()).rejects.toThrow("Network Error");
  });
});
