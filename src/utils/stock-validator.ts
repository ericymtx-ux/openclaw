export type StockMarket = "SH" | "SZ";

export interface StockCode {
  code: string;
  market: StockMarket;
  fullCode: string;
}

export interface ValidationResult {
  isValid: boolean;
  stock?: StockCode;
  errors: string[];
  warnings: string[];
}

const SH_PREFIXES = new Set(["6", "5", "9"]);
const SZ_PREFIXES = new Set(["0", "1", "3", "8"]);

const SIMILAR_CODE_PAIRS: [string, string][] = [
  ["600519", "600159"],
  ["000001", "600000"],
  ["688337", "688011"],
  ["300001", "600001"],
  ["000002", "600002"],
  ["600036", "600060"],
  ["601398", "601939"],
  ["000651", "600051"],
  ["300750", "300760"],
  ["002475", "002457"],
];

function validateFormat(stock: StockCode): string[] {
  const errors: string[] = [];

  const firstDigit = stock.code[0];
  if (stock.market === "SH" && !SH_PREFIXES.has(firstDigit)) {
    errors.push(
      `Shanghai stock code should start with 6, 5, or 9 (got '${firstDigit}')`,
    );
  }
  if (stock.market === "SZ" && !SZ_PREFIXES.has(firstDigit)) {
    errors.push(
      `Shenzhen stock code should start with 0, 1, or 3 (got '${firstDigit}')`,
    );
  }

  if (!/^\d{6}$/.test(stock.code)) {
    errors.push("Stock code must be exactly 6 digits");
  }

  return errors;
}

function checkSimilarCodes(stock: StockCode): string[] {
  const warnings: string[] = [];

  for (const [code1, code2] of SIMILAR_CODE_PAIRS) {
    if (stock.code === code1 || stock.code === code2) {
      const similar = stock.code === code1 ? code2 : code1;
      warnings.push(
        `Stock code ${stock.code} is similar to ${similar}. Please verify this is the correct stock.`,
      );
    }
  }

  const similarByDigitChange = findSimilarByDigitChange(stock.code);
  for (const similar of similarByDigitChange) {
    if (similar !== stock.code) {
      warnings.push(
        `Stock code ${stock.code} is similar to ${similar}. Please verify this is the correct stock.`,
      );
    }
  }

  return warnings;
}

function findSimilarByDigitChange(code: string): string[] {
  const similar: string[] = [];

  for (let i = 0; i < code.length; i++) {
    const digits = code.split("");
    for (const d of ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]) {
      if (digits[i] !== d) {
        digits[i] = d;
        const candidate = digits.join("");
        if (candidate !== code) {
          similar.push(candidate);
        }
      }
    }
  }

  return similar.slice(0, 3);
}

export function parseStockCode(input: string): StockCode | null {
  if (!input) {
    return null;
  }
  const normalized = input.trim().toUpperCase().replace(/．/g, ".");

  if (!normalized.includes(".")) {
    return null;
  }

  const parts = normalized.split(".");
  if (parts.length !== 2) {
    return null;
  }

  const code = parts[0];
  const suffix = parts[1];

  if (!/^\d{6}$/.test(code)) {
    return null;
  }

  let market: StockMarket | null = null;
  if (suffix === "SH" || suffix === "SS") {
    market = "SH";
  } else if (suffix === "SZ") {
    market = "SZ";
  }

  if (!market) {
    return null;
  }

  return {
    code,
    market,
    fullCode: `${code}.${suffix === "SS" ? "SH" : suffix}`,
  };
}

export function validateStockCode(input: string): ValidationResult {
  const result: ValidationResult = {
    isValid: false,
    errors: [],
    warnings: [],
  };

  const stock = parseStockCode(input);
  if (!stock) {
    result.errors.push(
      `Invalid stock code format: '${input}'. Expected format: '123456.SH' or '123456.SZ'`,
    );
    return result;
  }

  result.stock = stock;

  const formatErrors = validateFormat(stock);
  result.errors.push(...formatErrors);

  if (formatErrors.length === 0) {
    const warnings = checkSimilarCodes(stock);
    result.warnings.push(...warnings);
  }

  result.isValid = result.errors.length === 0;
  return result;
}

export async function checkStockExists(
  _code: string,
  _apiToken?: string,
): Promise<boolean> {
  return true;
}

export function formatStockCode(
  code: string,
  market: StockMarket,
  separator: "." | "-" = ".",
): string {
  return `${code}${separator}${market}`;
}

export function normalizeStockCode(input: string): string | null {
  const stock = parseStockCode(input);
  if (!stock) {
    return null;
  }
  return stock.fullCode;
}

export function guessMarket(code: string): StockMarket | null {
  const firstDigit = code[0];
  if (SH_PREFIXES.has(firstDigit)) {
    return "SH";
  }
  if (SZ_PREFIXES.has(firstDigit)) {
    return "SZ";
  }
  return null;
}
