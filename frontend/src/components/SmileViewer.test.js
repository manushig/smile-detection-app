import React from "react";
import { render, screen } from "@testing-library/react";
import SmileViewer from "./SmileViewer";

/**
 * SmileViewer Component Tests
 */

// Test: Should render placeholder text when no imageSrc is provided
test("renders 'No image' placeholder when imageSrc is null", () => {
  render(<SmileViewer imageSrc={null} />);
  expect(screen.getByText(/no image/i)).toBeInTheDocument();
});

// Test: Should render <img> tag with correct src and alt text when imageSrc is provided
test("renders image when imageSrc is provided", () => {
  const fakeUrl = "http://example.com/smile.jpg";
  render(<SmileViewer imageSrc={fakeUrl} />);
  const img = screen.getByAltText(/smile detection/i);
  expect(img).toBeInTheDocument();
  expect(img).toHaveAttribute("src", fakeUrl);
});

// Test: Image always has alt text for accessibility
test("image has correct alt text", () => {
  const fakeUrl = "http://example.com/smile.jpg";
  render(<SmileViewer imageSrc={fakeUrl} />);
  const img = screen.getByAltText(/smile detection/i);
  expect(img).toBeInTheDocument();
});
