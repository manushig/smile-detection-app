import axios from "axios";

/**
 * Base URL for the backend smile detection API.
 * In production, this should be set using environment variables (e.g., process.env.REACT_APP_API_URL).
 */
const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Starts the camera on the backend.
 * @returns {Promise<object>} Axios response from backend.
 * @throws {Error} Network or backend error.
 */
export async function startCamera() {
  try {
    const response = await axios.post(`${BASE_URL}/start_camera`);
    return response.data;
  } catch (error) {
    // Rethrow for UI handling
    throw error;
  }
}

/**
 * Stops the camera on the backend.
 * @returns {Promise<object>} Axios response from backend.
 * @throws {Error} Network or backend error.
 */
export async function stopCamera() {
  try {
    const response = await axios.post(`${BASE_URL}/stop_camera`);
    return response.data;
  } catch (error) {
    throw error;
  }
}

/**
 * Validates response status codes from the smile detection API.
 * Allows 200 (OK), 204 (No Content), and 500 (Internal Server Error) as "handled" responses.
 * @param {number} status - HTTP status code from the response
 * @returns {boolean} Whether the status is considered valid for processing
 */
export const validateSmileStatus = (status) =>
  status === 200 || status === 204 || status === 500;

/**
 * Polls the backend for smile detection on the current camera frame.
 * @returns {Promise<object>} Axios response, including image blob and headers.
 * @throws {Error} Network or backend error.
 */
export async function fetchSmileDetection() {
  try {
    const response = await axios.get(`${BASE_URL}/detect_smile`, {
      responseType: "blob",
      validateStatus: validateSmileStatus,
    });
    return response;
  } catch (error) {
    throw error;
  }
}
