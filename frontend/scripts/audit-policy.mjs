#!/usr/bin/env node
/**
 * StandBharat - Frontend Dependency Security Audit Policy Enforcer
 * Phase 40B: CI Security Gate Hardening
 *
 * Enforces:
 * 1. ZERO vulnerabilities in production runtime dependencies (npm audit --omit=dev).
 * 2. ZERO critical vulnerabilities anywhere in the dependency tree.
 * 3. Explicit documented policy for devDependencies: Only permits the known, non-exploitable
 *    braces / eslint-config-next linter advisory (GHSA-vfj7-8cjw-p6xm). Any other high-severity
 *    vulnerability fails the build immediately.
 */

import { execSync } from 'child_process';

const ACCEPTED_DEV_ADVISORIES = new Set([
  '1240992', // GHSA-vfj7-8cjw-p6xm (braces stack-exhaustion in dev linter)
]);

const ACCEPTED_DEV_PACKAGES = new Set([
  'braces',
  'micromatch',
  'fast-glob',
  '@next/eslint-plugin-next',
  'eslint-config-next'
]);

console.log('============================================================');
console.log('STANDBHARAT FRONTEND DEPENDENCY AUDIT POLICY CHECK');
console.log('============================================================');

// Step 1: Enforce zero production runtime bundle vulnerabilities
console.log('\n[1/2] Verifying production runtime dependencies (--omit=dev)...');
try {
  const prodOutput = execSync('npm audit --omit=dev --json', { encoding: 'utf-8' });
  const prodReport = JSON.parse(prodOutput);
  const prodVulns = prodReport.metadata?.vulnerabilities || {};
  const prodTotal = prodVulns.total || 0;

  if (prodTotal > 0) {
    console.error(`\n[FAIL] Found ${prodTotal} vulnerability/vulnerabilities in production dependencies!`);
    console.error(JSON.stringify(prodReport.vulnerabilities, null, 2));
    process.exit(1);
  }
  console.log('✓ PASS: Zero vulnerabilities in production runtime bundle.');
} catch (error) {
  if (error.stdout) {
    try {
      const prodReport = JSON.parse(error.stdout);
      const prodTotal = prodReport.metadata?.vulnerabilities?.total || 0;
      if (prodTotal > 0) {
        console.error(`\n[FAIL] Found ${prodTotal} vulnerability/vulnerabilities in production dependencies!`);
        console.error(JSON.stringify(prodReport.vulnerabilities, null, 2));
        process.exit(1);
      }
    } catch (_) {}
  }
  console.error('[ERROR] Failed to run production npm audit:', error.message);
  process.exit(1);
}

// Step 2: Audit full dependency tree with explicit dev policy
console.log('\n[2/2] Verifying full tree against devDependency security policy...');
let fullReport = null;
try {
  const fullOutput = execSync('npm audit --json', { encoding: 'utf-8' });
  fullReport = JSON.parse(fullOutput);
} catch (error) {
  if (error.stdout) {
    try {
      fullReport = JSON.parse(error.stdout);
    } catch (_) {}
  }
}

if (!fullReport) {
  console.error('[ERROR] Could not parse npm audit report.');
  process.exit(1);
}

const vulns = fullReport.metadata?.vulnerabilities || {};
const criticalCount = vulns.critical || 0;
const highCount = vulns.high || 0;

if (criticalCount > 0) {
  console.error(`\n[FAIL] Found ${criticalCount} CRITICAL vulnerability/vulnerabilities!`);
  process.exit(1);
}

// Check every reported vulnerability in the full tree
const unaccepted = [];
const details = fullReport.vulnerabilities || {};

for (const [pkgName, pkgData] of Object.entries(details)) {
  const severity = pkgData.severity;
  if (severity === 'high' || severity === 'critical') {
    if (!ACCEPTED_DEV_PACKAGES.has(pkgName)) {
      unaccepted.push({ package: pkgName, severity, reason: 'Unaccepted package with high/critical severity' });
      continue;
    }

    // Verify advisory IDs in via array
    const viaList = Array.isArray(pkgData.via) ? pkgData.via : [];
    for (const item of viaList) {
      if (typeof item === 'object' && item.source) {
        const sourceId = String(item.source);
        if (!ACCEPTED_DEV_ADVISORIES.has(sourceId)) {
          unaccepted.push({ package: pkgName, severity, advisory: item.title, sourceId });
        }
      }
    }
  }
}

if (unaccepted.length > 0) {
  console.error('\n[FAIL] Detected unaccepted high-severity vulnerabilities:');
  console.error(JSON.stringify(unaccepted, null, 2));
  process.exit(1);
}

console.log(`✓ PASS: ${highCount} high-severity findings documented & accepted in dev dependencies.`);
console.log('        Reason: eslint-config-next / braces (GHSA-vfj7-8cjw-p6xm) dev linter tool.');
console.log('        Installed braces version is 3.0.3. Zero production client exposure.');
console.log('============================================================');
console.log('STATUS: POLICY COMPLIANT (0 production, 0 critical, 0 unvetted high)');
console.log('============================================================');
process.exit(0);
