/**
 * Hypothesis Lab - Mathematical Engine Verification Script
 * Validates CDFs and statistical calculations against known statistical targets.
 */

const Stats = require('../scratch/hypothesis-lab/js/stats.js');

console.log("==========================================");
console.log("Starting Mathematical Solver Verification...");
console.log("==========================================\n");

let failures = 0;

// Test 1: Normal CDF
const testNormalCDF = () => {
  console.log("Testing Normal CDF...");
  const cases = [
    { z: 0, expected: 0.5 },
    { z: 1.96, expected: 0.9750 }, // Approx 95% two-tail bounds
    { z: -1.96, expected: 0.0250 },
    { z: 2.576, expected: 0.9950 } // Approx 99% two-tail bounds
  ];

  cases.forEach(c => {
    const calc = Stats.normalCDF(c.z);
    const diff = Math.abs(calc - c.expected);
    if (diff < 0.005) {
      console.log(`  Z: ${c.z.toFixed(3)} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [PASS]`);
    } else {
      console.log(`  Z: ${c.z.toFixed(3)} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [FAIL]`);
      failures++;
    }
  });
};

// Test 2: Student-t CDF
const testTCDF = () => {
  console.log("\nTesting Student's t CDF...");
  const cases = [
    { t: 0, df: 10, expected: 0.5 },
    { t: 2.228, df: 10, expected: 0.9750 }, // Critical value for df=10 at 0.05 two-tailed is ~2.228
    { t: -2.228, df: 10, expected: 0.0250 },
    { t: 1.96, df: 1000, expected: 0.9750 } // Converges to Z
  ];

  cases.forEach(c => {
    const calc = Stats.tCDF(c.t, c.df);
    const diff = Math.abs(calc - c.expected);
    if (diff < 0.005) {
      console.log(`  t: ${c.t.toFixed(3)}, df: ${c.df} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [PASS]`);
    } else {
      console.log(`  t: ${c.t.toFixed(3)}, df: ${c.df} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [FAIL]`);
      failures++;
    }
  });
};

// Test 3: Chi-Square CDF
const testChiSquareCDF = () => {
  console.log("\nTesting Chi-Square CDF...");
  const cases = [
    { x: 3.841, df: 1, expected: 0.9500 }, // Critical value for df=1 is 3.841
    { x: 5.991, df: 2, expected: 0.9500 }, // Critical value for df=2 is 5.991
    { x: 7.815, df: 3, expected: 0.9500 }, // Critical value for df=3 is 7.815
    { x: 9.488, df: 4, expected: 0.9500 }  // Critical value for df=4 is 9.488
  ];

  cases.forEach(c => {
    const calc = Stats.chiSquareCDF(c.x, c.df);
    const diff = Math.abs(calc - c.expected);
    if (diff < 0.005) {
      console.log(`  Chi2: ${c.x.toFixed(3)}, df: ${c.df} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [PASS]`);
    } else {
      console.log(`  Chi2: ${c.x.toFixed(3)}, df: ${c.df} -> Calc: ${calc.toFixed(4)} (Expected: ${c.expected.toFixed(4)}) [FAIL]`);
      failures++;
    }
  });
};

// Test 4: One-Sample t-test
const testOneSampleTTest = () => {
  console.log("\nTesting One-Sample t-test Calculations...");
  const data = [10, 12, 9, 15, 11, 13, 10]; // Mean: 11.4286, Std Dev: 1.9880
  const mu = 10;
  
  // Hand-calculated details:
  // df = 6
  // SE = 1.9880 / sqrt(7) = 0.7514
  // t = (11.4286 - 10) / 0.7514 = 1.9012
  // Two-tailed p-value (t=1.9012, df=6) is ~0.106
  
  const res = Stats.oneSampleTTest(data, mu, 'two-sided');
  
  const tDiff = Math.abs(res.statistic - 1.9012);
  const pDiff = Math.abs(res.pValue - 0.1060);
  
  if (tDiff < 0.01 && pDiff < 0.01) {
    console.log(`  One-Sample t-test: t-stat: ${res.statistic.toFixed(4)} (Expected: 1.9012), p-val: ${res.pValue.toFixed(4)} (Expected: 0.1060) [PASS]`);
  } else {
    console.log(`  One-Sample t-test: t-stat: ${res.statistic.toFixed(4)}, p-val: ${res.pValue.toFixed(4)} [FAIL]`);
    failures++;
  }
};

// Test 5: Independent t-test
const testIndependentTTest = () => {
  console.log("\nTesting Independent Two-Sample t-test...");
  const g1 = [12, 15, 11, 14, 13]; // Mean: 13.0, Var: 2.5
  const g2 = [18, 17, 21, 19];     // Mean: 18.75, Var: 2.9167
  
  // Independent Welch's t-test (EqualVar = false):
  // t-stat: -5.1970
  // df: 6.77
  // p-value: ~0.0013
  
  const res = Stats.independentTTest(g1, g2, false, 'two-sided');
  
  const tDiff = Math.abs(res.statistic - (-5.1970));
  const pDiff = Math.abs(res.pValue - 0.0013);
  
  if (tDiff < 0.05 && pDiff < 0.005) {
    console.log(`  Independent t-test (Welch): t-stat: ${res.statistic.toFixed(4)} (Expected: -5.1970), p-val: ${res.pValue.toFixed(4)} (Expected: 0.0013) [PASS]`);
  } else {
    console.log(`  Independent t-test (Welch): t-stat: ${res.statistic.toFixed(4)}, p-val: ${res.pValue.toFixed(4)} [FAIL]`);
    failures++;
  }
};

// Test 6: One-way ANOVA
const testANOVA = () => {
  console.log("\nTesting One-Way ANOVA...");
  const groups = [
    [4, 6, 8],     // Mean: 6
    [10, 12, 14],  // Mean: 12
    [2, 4, 6]      // Mean: 4
  ];
  // SSB = 3 * (6-7.33)^2 + 3 * (12-7.33)^2 + 3 * (4-7.33)^2 = 3*(1.77+21.8+11.1) = ~104 (approx exact 104)
  // SSW = (4+4+4) = 12
  // dfBetween = 2, dfWithin = 6
  // MSB = 104 / 2 = 52
  // MSW = 12 / 6 = 2
  // F = 52 / 2 = 26
  // p-value = 0.00115
  
  const res = Stats.oneWayAnova(groups);
  
  const fDiff = Math.abs(res.statistic - 26);
  const pDiff = Math.abs(res.pValue - 0.00115);
  
  if (fDiff < 0.01 && pDiff < 0.0005) {
    console.log(`  ANOVA One-Way: F-stat: ${res.statistic.toFixed(4)} (Expected: 26.0000), p-val: ${res.pValue.toFixed(5)} (Expected: 0.00115) [PASS]`);
  } else {
    console.log(`  ANOVA One-Way: F-stat: ${res.statistic.toFixed(4)}, p-val: ${res.pValue.toFixed(5)} [FAIL]`);
    failures++;
  }
};

// Run all tests
testNormalCDF();
testTCDF();
testChiSquareCDF();
testOneSampleTTest();
testIndependentTTest();
testANOVA();

console.log("\n==========================================");
if (failures === 0) {
  console.log("All Mathematical Tests PASSED Successfully!");
} else {
  console.log(`Mathematical Tests Completed with ${failures} FAILURES.`);
}
console.log("==========================================");
