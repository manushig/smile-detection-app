/**
 * SmileDetails component Tests.
 *
 * Covers all rendering cases for smile detection region and fallback message.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import SmileDetails from "./SmileDetails";

//
// Tests for SmileDetails rendering logic
//
describe("SmileDetails", () => {
  /**
   * Should display "No smile detected yet" if no smile detected and coords is null.
   */
  it('shows "No smile detected yet" if no smile', () => {
    render(<SmileDetails coords={null} smileDetected={false} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show region for smile when coords is an array.
   */
  it("shows region when smile is detected (array coords)", () => {
    const coords = [{ x: 100, y: 200, w: 50, h: 20 }];
    render(<SmileDetails coords={coords} smileDetected={true} />);
    expect(
      screen.getByText(/region: \[100, 200\] — 50×20 px/i)
    ).toBeInTheDocument();
  });

  /**
   * Should show region for smile when coords is an object.
   */
  it("shows region when smile is detected (object coords)", () => {
    const coords = { x: 1, y: 2, w: 3, h: 4 };
    render(<SmileDetails coords={coords} smileDetected={true} />);
    expect(screen.getByText(/region: \[1, 2\] — 3×4 px/i)).toBeInTheDocument();
  });

  /**
   * Should fallback to placeholder if coords is empty array.
   */
  it("shows 'No smile detected yet' if coords is empty array", () => {
    render(<SmileDetails coords={[]} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should fallback to placeholder if smileDetected true but coords is undefined.
   */
  it("shows 'No smile detected yet' if smileDetected true but coords undefined", () => {
    render(<SmileDetails coords={undefined} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should fallback to placeholder if smileDetected is false even when coords present.
   */
  it("shows 'No smile detected yet' if smileDetected false even with coords", () => {
    render(
      <SmileDetails
        coords={[{ x: 10, y: 10, w: 10, h: 10 }]}
        smileDetected={false}
      />
    );
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should fallback to placeholder if coords is unrelated type (e.g., string).
   */
  it("shows 'No smile detected yet' if coords is unrelated type", () => {
    render(<SmileDetails coords="string value" smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });
});
