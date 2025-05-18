import React from "react";

/**
 * Formats the bounding box/region information for display.
 * Accepts either an array with an object (from Haar cascade output) or a plain object.
 *
 * @param {Object|Array|null} coords - Detected smile bounding box, array or object, or null.
 * @returns {string|null} Formatted region string, or null if coords are invalid.
 */
function formatRegion(coords) {
  if (Array.isArray(coords) && coords.length > 0) {
    const box = coords[0];
    return `Region: [${box.x}, ${box.y}] — ${box.w}×${box.h} px`;
  }
  if (
    coords &&
    typeof coords === "object" &&
    "x" in coords &&
    "y" in coords &&
    "w" in coords &&
    "h" in coords
  ) {
    return `Region: [${coords.x}, ${coords.y}] — ${coords.w}×${coords.h} px`;
  }
  return null;
}

/**
 * SmileDetails
 * @param {Object} props
 * @param {Object|Array|null} props.coords - Coordinates for smile bounding box, or null.
 * @param {boolean} props.smileDetected - Whether a smile was detected in the current image.
 */
function SmileDetails({ coords, smileDetected }) {
  const regionString = formatRegion(coords);

  return (
    <div className="smile-details-wide">
      {smileDetected && regionString ? (
        <>
          <h2 className="smile-detected-header">😊 Smile detected!</h2>
          <div className="smile-region-info">{regionString}</div>
        </>
      ) : (
        <div className="no-smile-message">No smile detected yet</div>
      )}
    </div>
  );
}

export default SmileDetails;
