// This imports the spinning loader icon.
import { Loader2 } from "lucide-react";

// This fills the screen with a centred spinner while something loads.
export default function FullPageSpinner({ label = "Loading..." }) {
  // This returns the spinner layout.
  return (
    // This centres the content in the full screen height.
    <div className="flex min-h-screen items-center justify-center gap-3 text-slate-500">
      {/* This is the spinning icon; aria-hidden hides it from screen readers since the text says the same. */}
      <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
      {/* This is the text shown next to the spinner. */}
      <span>{label}</span>
    </div>
  );
}
