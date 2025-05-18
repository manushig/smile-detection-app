import React from "react";

/**
 * SmileViewer Component
 *
 * Displays the image from the latest smile detection, filling the parent area.
 * If no image is provided, a friendly placeholder message is shown.
 *
 * Props:
 * - imageSrc (string|null): URL to the detected smile image, or null if not available.
 *
 */
function SmileViewer({ imageSrc }) {
  return (
    <div className="smile-viewer-wide">
      {imageSrc ? (
        <img
          src={imageSrc}
          alt="Smile Detection"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            borderRadius: "8px",
            background: "#eaeaea",
          }}
        />
      ) : (
        <span className="no-image-placeholder">No image</span>
      )}
    </div>
  );
}

export default SmileViewer;
