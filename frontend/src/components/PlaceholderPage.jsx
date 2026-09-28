// This imports the "under construction" icon.
import { Construction } from "lucide-react";

// This is a temporary page for sections that later phases will build.
export default function PlaceholderPage({ title, description, phase }) {
  // This returns the placeholder layout.
  return (
    // This groups the heading and the notice.
    <section>
      {/* This is the page title. */}
      <h1 className="text-2xl font-bold">{title}</h1>
      {/* This is the dashed "coming soon" box. */}
      <div className="mt-6 flex items-start gap-3 rounded-xl border border-dashed border-slate-300 bg-white p-6 text-slate-600">
        {/* This is the icon. */}
        <Construction className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" aria-hidden="true" />
        {/* This is the explanation. */}
        <div>
          {/* This says what the page will do. */}
          <p>{description}</p>
          {/* This says which phase builds it. */}
          <p className="mt-1 text-sm text-slate-400">Coming in Phase {phase}.</p>
        </div>
      </div>
    </section>
  );
}
