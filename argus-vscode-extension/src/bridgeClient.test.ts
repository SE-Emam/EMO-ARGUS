import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  isLoopbackUrl,
  normalizeBridgeUrl,
  DEFAULT_BRIDGE_URL,
} from './bridgeClient';

describe('isLoopbackUrl', () => {
  it('returns true for http://127.0.0.1', () => {
    assert.equal(isLoopbackUrl('http://127.0.0.1'), true);
  });

  it('returns true for http://127.0.0.1 with port', () => {
    assert.equal(isLoopbackUrl('http://127.0.0.1:8765'), true);
  });

  it('returns true for http://localhost', () => {
    assert.equal(isLoopbackUrl('http://localhost'), true);
  });

  it('returns true for http://localhost with port', () => {
    assert.equal(isLoopbackUrl('http://localhost:8765'), true);
  });

  it('returns true for http://[::1]', () => {
    assert.equal(isLoopbackUrl('http://[::1]'), true);
  });

  it('returns true for http://[::1] with port', () => {
    assert.equal(isLoopbackUrl('http://[::1]:8765'), true);
  });

  it('returns false for external host', () => {
    assert.equal(isLoopbackUrl('http://example.com'), false);
  });

  it('returns false for https loopback (wrong protocol)', () => {
    assert.equal(isLoopbackUrl('https://127.0.0.1'), false);
  });

  it('returns false for https localhost', () => {
    assert.equal(isLoopbackUrl('https://localhost:8765'), false);
  });

  it('returns false for empty string', () => {
    assert.equal(isLoopbackUrl(''), false);
  });

  it('returns false for malformed URL', () => {
    assert.equal(isLoopbackUrl('not-a-url'), false);
  });

  it('returns false for bare hostname without protocol', () => {
    assert.equal(isLoopbackUrl('127.0.0.1:8765'), false);
  });

  it('returns false for ftp protocol on loopback', () => {
    assert.equal(isLoopbackUrl('ftp://127.0.0.1'), false);
  });
});

describe('normalizeBridgeUrl', () => {
  it('trims whitespace', () => {
    assert.equal(
      normalizeBridgeUrl('  http://127.0.0.1:8765  '),
      'http://127.0.0.1:8765'
    );
  });

  it('removes trailing slashes', () => {
    assert.equal(
      normalizeBridgeUrl('http://127.0.0.1:8765///'),
      'http://127.0.0.1:8765'
    );
  });

  it('removes a single trailing slash', () => {
    assert.equal(
      normalizeBridgeUrl('http://127.0.0.1:8765/'),
      'http://127.0.0.1:8765'
    );
  });

  it('preserves valid URL without trailing slash', () => {
    assert.equal(
      normalizeBridgeUrl('http://127.0.0.1:9999'),
      'http://127.0.0.1:9999'
    );
  });

  it('falls back to default for empty string', () => {
    assert.equal(normalizeBridgeUrl(''), DEFAULT_BRIDGE_URL);
  });

  it('falls back to default for whitespace-only string', () => {
    assert.equal(normalizeBridgeUrl('   '), DEFAULT_BRIDGE_URL);
  });

  it('trims and strips trailing slash together', () => {
    assert.equal(
      normalizeBridgeUrl('  http://localhost:8765/  '),
      'http://localhost:8765'
    );
  });
});