// This formatter shows numbers as Kenyan Shillings, e.g. "Ksh 100,000.00".
const kesFormatter = new Intl.NumberFormat("en-KE", {
  // This adds the currency symbol.
  style: "currency",
  // This selects Kenyan Shillings.
  currency: "KES",
  // This always shows two decimal places.
  minimumFractionDigits: 2,
});

// This formatter shows a date and time in Nairobi time, e.g. "28 Sep, 11:37".
const eatFormatter = new Intl.DateTimeFormat("en-KE", {
  // This converts from UTC to East Africa Time whatever the laptop's timezone is.
  timeZone: "Africa/Nairobi",
  // This shows the day number.
  day: "numeric",
  // This shows a short month name.
  month: "short",
  // This shows the hour with two digits.
  hour: "2-digit",
  // This shows the minutes with two digits.
  minute: "2-digit",
  // This uses the 24-hour clock.
  hour12: false,
});

// This turns any value into a number, or null if it is empty.
function toNumber(value) {
  // Empty values stay empty so we can show a dash.
  if (value === null || value === undefined || value === "") return null;
  // Number() is safe here because this is only for display; money maths stays on the server.
  return Number(value);
}

// This formats a money value; the API sends money as text like "100000.00".
export function formatKES(value) {
  // This converts the text to a number.
  const number = toNumber(value);
  // This shows a dash when there is no value yet.
  return number === null ? "—" : kesFormatter.format(number);
}

// This formats a money change with a plus sign for gains, e.g. "+Ksh 580.00".
export function formatSignedKES(value) {
  // This converts the text to a number.
  const number = toNumber(value);
  // This shows a dash when there is no value.
  if (number === null) return "—";
  // This adds "+" in front of gains; losses already show "-".
  return `${number > 0 ? "+" : ""}${kesFormatter.format(number)}`;
}

// This formats a percentage with a sign, e.g. "+1.25%".
export function formatPercent(value) {
  // This converts the text to a number.
  const number = toNumber(value);
  // This shows a dash when there is no value.
  if (number === null) return "—";
  // This adds "+" in front of gains and keeps two decimals.
  return `${number > 0 ? "+" : ""}${number.toFixed(2)}%`;
}

// This picks green for gains, red for losses, and grey for no change.
export function changeColor(value) {
  // This converts the text to a number.
  const number = toNumber(value);
  // Gains are green.
  if (number > 0) return "text-emerald-600";
  // Losses are red.
  if (number < 0) return "text-rose-600";
  // No change or no data is grey.
  return "text-slate-500";
}

// The API sends UTC times without a "Z", which browsers would wrongly read as local time.
export function parseUtc(isoString) {
  // Adding "Z" marks the time as UTC.
  return new Date(isoString.endsWith("Z") ? isoString : `${isoString}Z`);
}

// This formats an API timestamp in Nairobi time, e.g. "28 Sep, 11:37".
export function formatEAT(isoString) {
  // This shows a dash when there is no time.
  if (!isoString) return "—";
  // This converts from UTC and formats in EAT.
  return eatFormatter.format(parseUtc(isoString));
}
