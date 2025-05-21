/**
 * SmileDetails component tests.
 *
 * - Covers all rendering cases: object, array, empty, and invalid coords.
 * - Verifies "smile detected" and fallback messages.
 * - Follows professional commenting and docstring style.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import SmileDetails from "./SmileDetails";

describe("SmileDetails", () => {
  /**
   * Should show "No smile detected yet" if smileDetected is false and coords is null.
   */
  it('shows "No smile detected yet" for smileDetected=false and coords=null', () => {
    render(<SmileDetails coords={null} smileDetected={false} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show "No smile detected yet" if smileDetected is false and coords is present.
   */
  it('shows "No smile detected yet" for smileDetected=false even if coords present', () => {
    render(
      <SmileDetails coords={{ x: 1, y: 2, w: 3, h: 4 }} smileDetected={false} />
    );
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show "No smile detected yet" if coords is undefined.
   */
  it('shows "No smile detected yet" for smileDetected=true but coords is undefined', () => {
    render(<SmileDetails coords={undefined} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show "No smile detected yet" if coords is an empty array.
   */
  it('shows "No smile detected yet" for smileDetected=true but coords is empty array', () => {
    render(<SmileDetails coords={[]} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show "No smile detected yet" if coords is an unrelated type (like a string).
   */
  it('shows "No smile detected yet" for smileDetected=true but coords is a string', () => {
    render(<SmileDetails coords={"invalid"} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });

  /**
   * Should show "Smile detected!" and the region when coords is a single object.
   */
  it('shows "Smile detected!" and region string for object coords', () => {
    render(
      <SmileDetails
        coords={{ x: 5, y: 10, w: 20, h: 8 }}
        smileDetected={true}
      />
    );
    expect(screen.getByText(/😊 smile detected!/i)).toBeInTheDocument();
    expect(
      screen.getByText(/smile: top-left \[5, 10\], size: 20×8 px/i)
    ).toBeInTheDocument();
  });

  /**
   * Should show "Smile detected!" and regions for coords as array with one box.
   */
  it('shows "Smile detected!" and region string for single array coords', () => {
    render(
      <SmileDetails
        coords={[{ x: 7, y: 9, w: 14, h: 18 }]}
        smileDetected={true}
      />
    );
    expect(screen.getByText(/😊 smile detected!/i)).toBeInTheDocument();
    expect(
      screen.getByText(/smile: top-left \[7, 9\], size: 14×18 px/i)
    ).toBeInTheDocument();
  });

  /**
   * Should show all region strings for array of multiple boxes.
   */
  it("shows all region strings for multiple array coords", () => {
    const coords = [
      { x: 1, y: 2, w: 3, h: 4 },
      { x: 5, y: 6, w: 7, h: 8 },
    ];
    render(<SmileDetails coords={coords} smileDetected={true} />);
    expect(screen.getByText(/😊 smile detected!/i)).toBeInTheDocument();
    expect(
      screen.getByText(/smile 1: top-left \[1, 2\], size: 3×4 px/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/smile 2: top-left \[5, 6\], size: 7×8 px/i)
    ).toBeInTheDocument();
  });

  /**
   * Should not render region info if coords is a malformed object (missing keys).
   */
  it('shows "No smile detected yet" for malformed object coords', () => {
    render(<SmileDetails coords={{ x: 1, y: 2 }} smileDetected={true} />);
    expect(screen.getByText(/no smile detected yet/i)).toBeInTheDocument();
  });
});
