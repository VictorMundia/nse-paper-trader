// This is one summary box on the dashboard, e.g. "Total value: Ksh 100,000.00".
export default function StatCard({ icon: Icon, label, value, detail, detailClass = "text-slate-500", accent = "text-emerald-600" }) {
  // This returns the card layout.
  return (
    // This is the white card with a border.
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      {/* This row holds the label and its icon. */}
      <div className="flex items-center justify-between">
        {/* This is the label, e.g. "Cash available". */}
        <p className="text-sm text-slate-500">{label}</p>
        {/* This is the icon; the accent colour differs per card. */}
        <Icon className={`h-5 w-5 ${accent}`} aria-hidden="true" />
      </div>
      {/* This is the main value. */}
      <p className="mt-2 text-2xl font-semibold tracking-tight">{value}</p>
      {/* This is the optional small line under the value, e.g. "+0.25% since start". */}
      {detail && <p className={`mt-1 text-sm ${detailClass}`}>{detail}</p>}
    </div>
  );
}
