import React from "react";

/**
 * Formats bounding box/region information for display.
 * Handles arrays (for multiple boxes) and single object.
 *
 * @param {Object|Array|null} coords - Detected bounding boxes or null.
 * @returns {string[]} Array of formatted region strings (empty if invalid).
 */
function formatRegion(coords) {
  if (Array.isArray(coords) && coords.length > 0) {
    if (coords.length === 1) {
      const box = coords[0];
      return [
        `Smile: Top-left [${box.x}, ${box.y}], Size: ${box.w}×${box.h} px`,
      ];
    }
    return coords.map(
      (box, idx) =>
        `Smile ${idx + 1}: Top-left [${box.x}, ${box.y}], Size: ${box.w}×${
          box.h
        } px`
    );
  }
  if (
    coords &&
    typeof coords === "object" &&
    "x" in coords &&
    "y" in coords &&
    "w" in coords &&
    "h" in coords
  ) {
    return [
      `Smile: Top-left [${coords.x}, ${coords.y}], Size: ${coords.w}×${coords.h} px`,
    ];
  }
  return [];
}
/**
 * SmileDetails component
 * Displays smile detection result regions or fallback if not detected.
 *
 * @param {Object} props
 * @param {Object|Array|null} props.coords - Smile bounding box(es), or null.
 * @param {boolean} props.smileDetected - Whether smile(s) detected in image.
 */
function SmileDetails({ coords, smileDetected }) {
  const regionStrings = formatRegion(coords);

  return (
    <div className="smile-details-wide">
      {smileDetected && regionStrings.length > 0 ? (
        <>
          <h2 className="smile-detected-header">😊 Smile detected!</h2>
          <div className="smile-region-info">
            {regionStrings.map((str, i) => (
              <div key={i}>{str}</div>
            ))}
          </div>
        </>
      ) : (
        <div className="no-smile-message">No smile detected yet</div>
      )}
    </div>
  );
}

export default SmileDetails;
