/**
 * Smile detection API client Tests.
 */

import axios from "axios";
import { fetchSmileDetection, validateSmileStatus } from "./SmileApi";

// Mock axios to prevent actual HTTP requests and control responses
jest.mock("axios");

//
// Tests for validateSmileStatus utility
//
describe("validateSmileStatus", () => {
  // Should return true for accepted statuses
  it("returns true for 200", () => {
    expect(validateSmileStatus(200)).toBe(true);
  });

  it("returns true for 204", () => {
    expect(validateSmileStatus(204)).toBe(true);
  });

  it("returns true for 500", () => {
    expect(validateSmileStatus(500)).toBe(true);
  });

  // Should return false for unexpected statuses
  it("returns false for 404", () => {
    expect(validateSmileStatus(404)).toBe(false);
  });

  it("returns false for 400", () => {
    expect(validateSmileStatus(400)).toBe(false);
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
   * Should call /detect/opencv if model is not 'dlib'
   */
  it("calls /detect/opencv by default", async () => {
    axios.get.mockResolvedValue({ status: 200, data: "blob" });

    await fetchSmileDetection("opencv");

    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("/detect/opencv"),
      expect.objectContaining({
        responseType: "blob",
        validateStatus: expect.any(Function),
      })
    );
  });

  /**
   * Should call /detect/dlib if model is 'dlib'
   */
  it("calls /detect/dlib if model is 'dlib'", async () => {
    axios.get.mockResolvedValue({ status: 200, data: "blob" });

    await fetchSmileDetection("dlib");

    expect(axios.get).toHaveBeenCalledWith(
      expect.stringContaining("/detect/dlib"),
      expect.any(Object)
    );
  });

  /**
   * Should resolve with the response when axios call is successful
   */
  it("returns response on success", async () => {
    const mockResponse = { status: 200, data: "blob" };
    axios.get.mockResolvedValue(mockResponse);

    const response = await fetchSmileDetection("opencv");
    expect(response).toBe(mockResponse);
  });

  /**
   * Should propagate errors from axios (e.g., network error)
   */
  it("handles network errors", async () => {
    axios.get.mockRejectedValue(new Error("Network Error"));

    await expect(fetchSmileDetection("opencv")).rejects.toThrow(
      "Network Error"
    );
  });
});
