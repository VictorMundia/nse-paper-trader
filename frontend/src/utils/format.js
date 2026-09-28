// This formatter shows numbers as Kenyan Shillings, e.g. "Ksh 100,000.00".
const kesFormatter = new Intl.NumberFormat("en-KE", {
  // This adds the currency symbol.
  style: "currency",
  // This selects Kenyan Shillings.
  currency: "KES",
  // This always shows two decimal places.
  minimumFractionDigits: 2,
});

// This formats a money value; the API sends money as text like "100000.00".
export function formatKES(value) {
  // This shows a dash when there is no value yet.
  if (value === null || value === undefined || value === "") return "—";
  // Number() is safe here because this is only for display; maths stays on the server.
  return kesFormatter.format(Number(value));
}
