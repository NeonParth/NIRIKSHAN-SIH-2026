export function ProvenanceBanner() {
  return (
    <div
      className="border border-amber-300/80 bg-amber-50/90 text-amber-950 px-4 py-2.5 rounded-lg text-xs font-medium leading-relaxed shadow-sm my-4"
      role="status"
      data-testid="provenance-banner"
    >
      <span className="font-bold text-amber-900">Demo data only.</span> Synthetic demonstration data. SYNTHETIC records are not official MPLADS data. Risk scores indicate potential anomalies for verification; they do not establish fraud or wrongdoing.
    </div>
  );
}
