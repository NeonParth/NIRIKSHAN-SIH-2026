import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProvenanceBanner } from "../src/components/Dashboard/ProvenanceBanner";
import { RiskBadge } from "../src/components/RiskAnalysis/Badges";
import { AppShell } from "../src/components/Navigation/AppShell";

describe("provenance and risk UI", () => {
  it("shows synthetic demo disclaimer", () => {
    render(<ProvenanceBanner />);
    expect(screen.getByTestId("provenance-banner")).toHaveTextContent("Synthetic demonstration data");
    expect(screen.getByTestId("provenance-banner")).toHaveTextContent("not official MPLADS");
    expect(screen.getByTestId("provenance-banner")).toHaveTextContent("do not establish fraud");
  });

  it("renders risk level and score", () => {
    render(<RiskBadge level="HIGH" score={82} />);
    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("82/100")).toBeInTheDocument();
  });

  it("renders primary navigation", () => {
    render(
      <MemoryRouter>
        <AppShell />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Investigation" })).toBeInTheDocument();
  });
});
