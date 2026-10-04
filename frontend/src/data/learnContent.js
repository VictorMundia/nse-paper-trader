// These are the lessons on the Learn page; each has a title, a one-line summary, and paragraphs.
export const LESSONS = [
  {
    id: "nse",
    title: "What is the Nairobi Securities Exchange?",
    summary: "The marketplace where shares of Kenyan companies are bought and sold.",
    paragraphs: [
      "The Nairobi Securities Exchange (NSE) is Kenya's stock exchange. Companies such as Safaricom, Equity Group, and KCB list their shares there so the public can invest in them.",
      "The NSE is regulated by the Capital Markets Authority (CMA), which protects investors and makes sure listed companies share accurate information.",
      "Trading happens on weekdays during the day, Nairobi time. Prices change as buyers and sellers agree on deals.",
    ],
  },
  {
    id: "shares",
    title: "Shares, tickers, and prices",
    summary: "A share is a small piece of ownership in a company.",
    paragraphs: [
      "When you buy a share you own a tiny part of that company. If the company grows and makes profits, its shares usually become more valuable.",
      "Each company has a short code called a ticker. SCOM is Safaricom, EQTY is Equity Group, and KCB is KCB Group.",
      "The price is what the most recent buyer paid for one share. The change shows how much it moved, in shillings and as a percentage.",
    ],
  },
  {
    id: "orders",
    title: "How buying and selling works",
    summary: "A market order buys or sells straight away at the current price.",
    paragraphs: [
      "This simulator uses market orders: your trade executes immediately at the latest price. Cost = price × number of shares.",
      "Buying moves cash out of your account and shares in. Selling does the reverse. You can only sell shares you already own.",
      "In real life you need a CDS account (held at the Central Depository and Settlement Corporation) and a licensed stockbroker or investment app to trade on the NSE.",
    ],
  },
  {
    id: "profit",
    title: "Average cost and profit or loss",
    summary: "Your profit depends on what you paid, not just today's price.",
    paragraphs: [
      "If you buy the same stock several times at different prices, your average buy price is the total you paid divided by the number of shares.",
      "Unrealised profit or loss = (current price − average buy price) × shares held. It is only on paper and changes as the price moves.",
      "Realised profit or loss = (sell price − average buy price) × shares sold. It is locked in once you sell.",
    ],
  },
  {
    id: "risk",
    title: "Risk, volatility, and diversification",
    summary: "Prices go down as well as up; spreading your money reduces risk.",
    paragraphs: [
      "Volatility is how much a price moves around. A volatile stock can rise quickly but can also fall quickly.",
      "Diversification means spreading your money across several companies and sectors (for example banks, telecoms, and manufacturing). If one company does badly, the others soften the blow.",
      "Avoid putting most of your money into a single stock, and avoid buying or selling in a panic after one day's move.",
    ],
  },
  {
    id: "costs",
    title: "Real-world costs and dividends",
    summary: "Real trades cost money, and some companies pay you to hold their shares.",
    paragraphs: [
      "This simulator charges no fees. Real NSE trades include brokerage commission and regulatory levies, roughly around 2% of each trade for small investors. Check current rates with a licensed broker.",
      "Fees mean that trading very often can eat into your returns, which is one reason long-term investing is popular.",
      "Some companies share profits with shareholders as dividends, usually once or twice a year. Dividends are not included in this simulator.",
    ],
  },
];

// These are short definitions for the glossary.
export const GLOSSARY = [
  { term: "Bull market", definition: "A period when prices are generally rising." },
  { term: "Bear market", definition: "A period when prices are generally falling." },
  { term: "Blue-chip stock", definition: "A share in a large, well-established company, such as Safaricom." },
  { term: "Capital gain", definition: "Profit from selling a share for more than you paid." },
  { term: "Dividend", definition: "A share of a company's profit paid to its shareholders." },
  { term: "Liquidity", definition: "How easily a share can be bought or sold without moving its price much." },
  { term: "Market capitalisation", definition: "Share price × number of shares: the total market value of a company." },
  { term: "NASI", definition: "NSE All Share Index: tracks the value of all shares listed on the NSE." },
  { term: "Portfolio", definition: "All the investments you hold, plus your cash." },
  { term: "Volume", definition: "The number of shares traded in a period." },
];

// These are the self-check questions; "answer" is the index of the correct option.
export const QUIZ = [
  {
    question: "You buy 100 shares at KES 40, then 100 more at KES 50. What is your average buy price?",
    options: ["KES 40", "KES 45", "KES 50", "KES 90"],
    answer: 1,
    explanation: "Total paid = 100 × 40 + 100 × 50 = KES 9,000 for 200 shares. 9,000 ÷ 200 = KES 45.",
  },
  {
    question: "Your shares have risen in price but you have not sold them. What kind of profit is this?",
    options: ["Realised profit", "Unrealised profit", "A dividend", "A capital loss"],
    answer: 1,
    explanation: "Profit on shares you still hold is unrealised: it exists only on paper until you sell.",
  },
  {
    question: "Which portfolio is the most diversified?",
    options: ["All money in Safaricom", "Half in KCB, half in Equity", "Spread across a bank, a telecom, and a manufacturer", "All money kept as cash"],
    answer: 2,
    explanation: "Spreading money across different companies and sectors reduces the impact if one of them does badly.",
  },
  {
    question: "What does the ticker SCOM stand for on the NSE?",
    options: ["Standard Chartered", "Safaricom", "Sameer Africa", "Stanbic"],
    answer: 1,
    explanation: "SCOM is Safaricom's ticker. Standard Chartered is SCBK and Stanbic is SBIC.",
  },
  {
    question: "Who regulates Kenya's capital markets to protect investors?",
    options: ["Central Bank of Kenya", "Kenya Revenue Authority", "Capital Markets Authority", "Communications Authority"],
    answer: 2,
    explanation: "The Capital Markets Authority (CMA) regulates the NSE, stockbrokers, and listed companies.",
  },
];
