# Test doubles

A test double replaces a dependency with a controlled substitute. Keep the code that owns the behavior real.

Use substitutes for external services, clocks, randomness, or costly resources when needed for isolation and repeatability. Prefer a supported isolated test database for database semantics. An in-memory fake cannot establish SQL constraints, transaction behavior, or migration correctness.

Inject dependencies through existing interfaces. If no suitable interface exists, add the smallest boundary needed by the current behavior. Avoid redesigning the application merely to simplify a mock. Give external operations clear names and input/output types rather than adding a generic test-only dispatcher.

Make substitutes match the actual dependency contract, including relevant failures. Reset their state between tests. Do not mock internal modules simply to assert that the implementation followed a chosen sequence.

Interaction assertions are useful when the external interaction is itself required behavior. For example, a retry limit can require checking how many external attempts occurred. Also assert the caller-visible result or failure. Do not forbid all call-count assertions or treat them as sufficient for unrelated business behavior.

Never contact production services or use real customer data to make a test pass. If a faithful substitute cannot prove a requirement within the permitted environment, record the limitation instead of claiming integration coverage.
