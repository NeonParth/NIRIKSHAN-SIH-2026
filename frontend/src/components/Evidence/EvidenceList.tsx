import type { EvidenceRead, RiskEvidenceRead } from "../../types/api";
import { SourceBadge, VerificationBadge } from "../RiskAnalysis/Badges";

export function EvidenceList({
  evidence,
  links,
}: {
  evidence?: EvidenceRead[];
  links?: RiskEvidenceRead[];
}) {
  const items =
    links?.map((link) => ({
      id: link.evidence_id,
      type: link.evidence?.evidence_type ?? "EVIDENCE",
      uri: link.evidence?.storage_uri ?? "",
      explanation: link.explanation,
      source: link.evidence?.data_source,
      status: link.evidence?.verification_status,
    })) ??
    evidence?.map((item) => ({
      id: item.id,
      type: item.evidence_type,
      uri: item.storage_uri,
      explanation: "",
      source: item.data_source,
      status: item.verification_status,
    })) ??
    [];

  if (!items.length) {
    return <p className="text-sm text-slate-600">No evidence records are linked yet.</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="rounded border border-slate-200 bg-white p-3 text-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-semibold text-navy-900">{item.type.split("_").join(" ")}</span>
            {item.source ? <SourceBadge source={item.source} /> : null}
            {item.status ? <VerificationBadge status={item.status} /> : null}
          </div>
          {item.explanation ? <p className="mt-1 text-slate-600">{item.explanation}</p> : null}
          <p className="mt-1 break-all text-xs text-slate-500">{item.uri}</p>
        </li>
      ))}
    </ul>
  );
}
