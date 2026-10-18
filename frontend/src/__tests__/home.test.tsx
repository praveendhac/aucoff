import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { HomeView } from "@/components/home-view";

test("home view shows the product name and the tenant", () => {
  render(<HomeView tenantId="t-1" signOut={<button>Sign out</button>} />);
  expect(screen.getByRole("heading", { name: "AUCoFF" })).toBeInTheDocument();
  expect(screen.getByText("tenant t-1")).toBeInTheDocument();
});
