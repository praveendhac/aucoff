import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Home from "@/app/page";

test("home page shows the product name", () => {
  render(<Home />);
  expect(screen.getByRole("heading", { name: "AUCoFF" })).toBeInTheDocument();
});
