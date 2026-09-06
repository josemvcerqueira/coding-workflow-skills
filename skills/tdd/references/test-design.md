# Test design

Test the contract that callers depend on. Use real implementation behind that boundary. Private helper structure is not a contract. A refactor that preserves behavior should not require rewriting assertions about internal call order.

Choose a known expected result from the requirement, a worked example, or an independently established invariant. Do not copy the production algorithm into the expected-value calculation. A passing comparison between two copies of the same defect proves little.

For example, if a documented fee rule charges 3 units for each started block of 10 items, use this case:

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { packingFee } from './packing-fee.js';

test('11 items require two packing blocks', () => {
  assert.equal(packingFee(11), 6);
});
```

The result comes from two blocks at 3 units each. The test does not repeat the rounding algorithm. Add separate cases for other required behavior, such as zero items, only when the contract defines it.

Keep each test about one outcome. Multiple assertions can describe that outcome. Use clear setup, action, and result. Await asynchronous work. Isolate fixtures and restore replaced clocks or dependencies so test order cannot change results.

Use in-process component or integration tests when they prove interaction that an isolated function test cannot. A test can cross several modules without starting the application. Inspect runner configuration; browser suites may start a server automatically. Respect the implementation stage's command restrictions and record deferred live checks.

Prefer observing persisted behavior through the supported read interface. Direct database assertions are appropriate when the database schema, constraint, or migration is the contract under test. Do not impose a blanket ban that hides the actual requirement.

Use snapshots only for intentional, stable output contracts that can be meaningfully inspected. Avoid large snapshots that obscure the result being tested. Repeated green runs, coverage percentages, and mock-call assertions alone do not prove the required behavior.
