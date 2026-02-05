import { describe, expect, it } from "vitest";
import {
  validateStockCode,
  normalizeStockCode,
  formatStockCode,
  guessMarket,
  parseStockCode,
} from "./stock-validator.js";

describe("validateStockCode", () => {
  it("validates correct SH stock codes", () => {
    const result = validateStockCode("600519.SH");
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.stock?.code).toBe("600519");
    expect(result.stock?.market).toBe("SH");
  });

  it("validates correct SZ stock codes", () => {
    const result = validateStockCode("000001.SZ");
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.stock?.code).toBe("000001");
    expect(result.stock?.market).toBe("SZ");
  });

  it("validates STAR market codes (688 prefix)", () => {
    const result = validateStockCode("688337.SH");
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("validates ChiNext codes (300 prefix)", () => {
    const result = validateStockCode("300750.SZ");
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("validates BSE codes (8 prefix)", () => {
    const result = validateStockCode("833454.SZ");
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it("rejects invalid format without market suffix", () => {
    const result = validateStockCode("600519");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it("rejects invalid format with wrong suffix", () => {
    const result = validateStockCode("600519.US");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it("rejects short code", () => {
    const result = validateStockCode("6005.SH");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0]).toContain("Invalid stock code format");
  });

  it("rejects long code", () => {
    const result = validateStockCode("6005199.SH");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0]).toContain("Invalid stock code format");
  });

  it("rejects code with letters", () => {
    const result = validateStockCode("60051A.SH");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it("rejects SZ code with SH prefix", () => {
    const result = validateStockCode("600000.SZ");
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("Shenzhen stock code should start with");
  });

  it("rejects SH code with SZ prefix", () => {
    const result = validateStockCode("000001.SH");
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("Shanghai stock code should start with");
  });

  it("accepts lowercase input", () => {
    const result = validateStockCode("600519.sh");
    expect(result.isValid).toBe(true);
    expect(result.stock?.market).toBe("SH");
  });

  it("accepts SS suffix for Shanghai", () => {
    const result = validateStockCode("600519.SS");
    expect(result.isValid).toBe(true);
    expect(result.stock?.market).toBe("SH");
  });

  it("handles fullwidth dot", () => {
    const result = validateStockCode("600519．SH");
    expect(result.isValid).toBe(true);
    expect(result.stock?.code).toBe("600519");
  });
});

describe("normalizeStockCode", () => {
  it("normalizes valid SH code", () => {
    expect(normalizeStockCode("600519.SH")).toBe("600519.SH");
  });

  it("normalizes valid SZ code", () => {
    expect(normalizeStockCode("000001.SZ")).toBe("000001.SZ");
  });

  it("normalizes lowercase", () => {
    expect(normalizeStockCode("600519.sh")).toBe("600519.SH");
  });

  it("normalizes SS to SH", () => {
    expect(normalizeStockCode("600519.SS")).toBe("600519.SH");
  });

  it("returns null for invalid code", () => {
    expect(normalizeStockCode("invalid")).toBeNull();
  });
});

describe("formatStockCode", () => {
  it("formats with dot separator", () => {
    expect(formatStockCode("600519", "SH")).toBe("600519.SH");
  });

  it("formats with dash separator", () => {
    expect(formatStockCode("600519", "SH", "-")).toBe("600519-SH");
  });
});

describe("guessMarket", () => {
  it("guesses SH market for 6 prefix", () => {
    expect(guessMarket("600519")).toBe("SH");
  });

  it("guesses SH market for 9 prefix", () => {
    expect(guessMarket("688011")).toBe("SH");
  });

  it("guesses SH market for 5 prefix", () => {
    expect(guessMarket("500500")).toBe("SH");
  });

  it("guesses SZ market for 0 prefix", () => {
    expect(guessMarket("000001")).toBe("SZ");
  });

  it("guesses SZ market for 3 prefix", () => {
    expect(guessMarket("300750")).toBe("SZ");
  });

  it("guesses SZ market for 1 prefix", () => {
    expect(guessMarket("100123")).toBe("SZ");
  });

  it("returns null for invalid prefix", () => {
    expect(guessMarket("700519")).toBeNull();
  });
});

describe("parseStockCode", () => {
  it("parses SH code", () => {
    const result = parseStockCode("600519.SH");
    expect(result).not.toBeNull();
    expect(result?.code).toBe("600519");
    expect(result?.market).toBe("SH");
    expect(result?.fullCode).toBe("600519.SH");
  });

  it("parses SZ code", () => {
    const result = parseStockCode("000001.SZ");
    expect(result).not.toBeNull();
    expect(result?.code).toBe("000001");
    expect(result?.market).toBe("SZ");
    expect(result?.fullCode).toBe("000001.SZ");
  });

  it("returns null for invalid format", () => {
    expect(parseStockCode("600519")).toBeNull();
    expect(parseStockCode("600519.SH.SZ")).toBeNull();
    expect(parseStockCode("ABC123.SH")).toBeNull();
  });
});

describe("common mistake detection", () => {
  it("warns about 688337 vs 688011", () => {
    const result = validateStockCode("688011.SH");
    expect(result.isValid).toBe(true);
    expect(result.warnings.length).toBeGreaterThan(0);
    expect(result.warnings[0]).toContain("688337");
  });

  it("warns about 000001 vs 600000", () => {
    const result = validateStockCode("600000.SH");
    expect(result.isValid).toBe(true);
    expect(result.warnings.length).toBeGreaterThan(0);
    expect(result.warnings[0]).toContain("000001");
  });

  it("warns about single digit changes", () => {
    const result = validateStockCode("600510.SH");
    expect(result.isValid).toBe(true);
    expect(result.warnings.some((w) => w.includes("similar"))).toBe(true);
  });
});

describe("edge cases", () => {
  it("handles empty string", () => {
    const result = validateStockCode("");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it("handles whitespace", () => {
    const result = validateStockCode("  600519.SH  ");
    expect(result.isValid).toBe(true);
  });

  it("handles null/undefined gracefully", () => {
    const result = validateStockCode(null as unknown as string);
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
});
