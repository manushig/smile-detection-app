import axios from "axios";

/**
 * Base URL for the backend smile detection API.
 * In production, this should be set using environment variables (e.g., process.env.REACT_APP_API_URL).
 */
const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Validates response status codes from the smile detection API.
 * Allows 200 (OK), 204 (No Content), and 500 (Internal Server Error) as "handled" responses.
 * @param {number} status - HTTP status code from the response
 * @returns {boolean} Whether the status is considered valid for processing
 */
export const validateSmileStatus = (status) =>
  status === 200 || status === 204 || status === 500;

/**
 * Calls the smile detection endpoint on the backend.
 *
 * @param {string} model - The model type to use for detection ("dlib" or "opencv").
 * @returns {Promise<object>} Axios response containing the smile detection result as a blob.
 * @throws {Error} Any error from the network or request.
 */
export const fetchSmileDetection = async (model) => {
  const endpoint = model === "dlib" ? "/detect/dlib" : "/detect/opencv";
  const url = `${BASE_URL}${endpoint}`;
  return axios.get(url, {
    responseType: "blob",
    validateStatus: validateSmileStatus,
  });
};
