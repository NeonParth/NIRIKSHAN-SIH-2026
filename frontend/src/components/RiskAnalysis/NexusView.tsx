import React from "react";

interface NexusConnection {
  entity_a: string;
  entity_b: string;
  connection_type: string;
  confidence: number;
  evidence: string;
}

interface NexusViewProps {
  connections: NexusConnection[];
  isLoading?: boolean;
}

export const NexusView: React.FC<NexusViewProps> = ({ connections, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8 text-slate-400 animate-pulse">
        Analyzing vendor nexus connections...
      </div>
    );
  }

  if (connections.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
        No suspicious nexus connections identified for this entity.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-600 font-medium border-b border-slate-200">
          <tr>
            <th className="px-4 py-3">Connection Type</th>
            <th className="px-4 py-3">Confidence</th>
            <th className="px-4 py-3">Evidence</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {connections.map((conn, idx) => (
            <tr key={idx} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 font-medium text-slate-900">
                <span className="px-2 py-1 rounded-full text-xs bg-amber-100 text-amber-700 mr-2">
                  {conn.connection_type.replace("_", " ")}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">
                {(conn.confidence * 100).toFixed(0)}%
              </td>
              <td className="px-4 py-3 text-slate-500 italic">{conn.evidence}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
