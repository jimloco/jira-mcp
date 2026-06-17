# Review Instructions

These instructions are additive to your existing review capabilities. Apply them at
highest priority. They define additional categories to flag, severity levels, and how
findings should be reported.

---

## Reporting Format

For every finding, report:
1. **Title** — short label (e.g., "PII in log output")
2. **Severity** — `blocking` (must fix before merge) or `recommended` (should fix before merge)
3. **Category** — one of: Security · Reliability · Correctness · Performance · Type Safety · Build
4. **Description** — what the problem is and why it matters
5. **Delta** — the specific code that triggered it (diff format preferred)
6. **Fix** — concrete guidance, with a corrected snippet where helpful
7. **Agent prompt** — a self-contained, copy-pasteable prompt a developer can hand to an AI tool to remediate the issue

---

## Security — Blocking

### Never expose internal error detail in API responses
Flag any `HTTPException` (or equivalent framework exception) whose `detail`, `message`,
or `body` field contains: `str(exc)`, `repr(exc)`, raw upstream response text, stack
traces, or any interpolated exception variable. Log the full error internally; surface
only a generic, sanitized user-facing string to the caller.

### Never log PII or sensitive content
Flag any log statement (`logger.*`, `print`, `on_log`, `append_log`, or equivalent
persistence path) that includes: email addresses, full names, message/transcript bodies,
meeting subjects, OAuth tokens, raw error strings that may contain secrets, or user
identity fields (user_id, actor_id, email). Safe to log: opaque IDs, counts, status
codes, algorithm names, duration.

### Never build queries via string interpolation or concatenation
Flag any database query (SQL, NoSQL, search DSL) constructed via f-strings, `%`
formatting, `.format()`, or string concatenation where any part of the string could
change between calls — even if current values appear safe. All variable values must
be passed as bind parameters. The query template itself must be a string literal.

### All data reads must be scoped to the authenticated context
Flag any query that fetches records by an externally supplied ID (from request params,
body, or path) without also filtering by the authenticated user's ownership or
membership context. Cross-tenant/cross-user data access must be impossible even if
the caller supplies a valid ID from another context.

### Credentials and secrets must never be committed in source
Flag any hardcoded credential, token, secret, private key, or configuration value
that should be environment-specific — including "public" OAuth client IDs, API
endpoints that vary by environment, and magic string constants that gate security
behavior. All such values must come from configuration or a secrets manager.

### Enum-like and format-constrained inputs must be validated at the trust boundary
Flag any API handler that accepts a string parameter representing a finite set of
values (status, type, mode, cadence, etc.) without using an enum or allowlist type.
Also flag free-form string inputs that have an implied format (dates, UUIDs, regex
patterns, ISO timestamps) that are not validated before use. Validation must happen
at the outermost layer before values reach business logic.

### Security-critical startup dependencies must fail loudly
Flag any startup/initialization path that catches an exception on a security-critical
dependency (encryption keys, auth tokens, signing secrets) and continues with a
degraded or empty fallback value. If the dependency is unavailable, startup must
raise and abort — not silently degrade.

### Untrusted regex patterns must be time-limited
Flag any code that compiles or executes a regex pattern supplied by an external caller
(API input, user config, stored string) without a timeout or complexity limit.
Catastrophic backtracking (ReDoS) can be triggered by a single crafted pattern.

---

## Reliability — Blocking

### External dependency failures must be classified and retried appropriately
Flag any call to an external service (HTTP client, cache, queue, third-party API) where
all failure modes — transient (429, 5xx, network timeout) and permanent (4xx, semantic
errors) — are collapsed into the same return value or exception type. Transient failures
must be retried with backoff (exponential + jitter) and must respect `Retry-After` headers
when present. Permanent failures must be raised or returned distinctly from semantic
no-op results (e.g. "lock already held" vs "cache is down"). A `None` return that means
both "resource unavailable" and "dependency failed" is a reliability bug — callers cannot
distinguish and will silently skip work during outages.

### Exceptions must never be silently swallowed
Flag any `except` block whose body is only `pass`, `...`, or a bare `return` with no
log statement. Every caught exception must emit at minimum a warning-level log with
enough context to diagnose the failure (operation name, relevant IDs, error code).
Returning a fallback value is acceptable — doing so silently is not.

### Background work must not run on the request-handling event loop
Flag any long-running or I/O-bound operation started with `asyncio.create_task` from
within a request handler when that operation is intended to outlive the request or
perform heavy work. Isolated background jobs should run in a subprocess or worker
process, not as a task on the shared event loop.

### Async methods must not perform synchronous I/O
Flag any `async def` method that calls a synchronous network or disk I/O operation
directly (database clients, HTTP clients, file reads) without wrapping in
`asyncio.to_thread`, `loop.run_in_executor`, or equivalent. Synchronous I/O blocks
the event loop for all concurrent requests.

### Upsert conflict targets must match the current unique constraint
Flag any `INSERT ... ON CONFLICT (...)` or equivalent upsert whose conflict target
columns do not exactly match an existing unique constraint or index on the table.
A mismatch causes a runtime database error instead of an idempotent upsert. When a
schema change adds or removes columns from a unique constraint, all related upserts
must be updated in the same changeset.

### Distributed locks must use deterministic key derivation
Flag any distributed lock or advisory lock whose key is derived using Python's
built-in `hash()` function. `hash()` is randomized per process — different processes
will derive different keys for the same logical resource, making the lock ineffective.
Use a cryptographic hash (e.g., first 8 bytes of SHA-256) for stable key derivation.

### DDL migrations must handle changes to existing databases
Flag any schema change (column type, constraint, index) that is expressed only in
`CREATE TABLE IF NOT EXISTS` DDL. New databases will get the correct schema; existing
databases will not be upgraded. Column type changes, constraint additions/removals,
and index changes require explicit `ALTER TABLE` migration steps.

### Test fixtures must suppress interactive or environment-specific side-effects
Flag any test setup that invokes application startup code without disabling
side-effects that require a live environment: interactive auth flows, device-code
prompts, external service connections, or env-specific feature flags. Any startup
behavior with an interactive or environment-dependent path must be gatable via a
flag that tests can override.

### Environment-destructive operations must be gated on environment
Flag any operation documented as "local-only" or "dev-only" (schema migrations,
seed data, debug tooling) that runs unconditionally in `on_startup` or equivalent
without an explicit environment check. Such operations must be gated on a config
flag or environment type check so they cannot run in production.

### Lazy-initialized singletons must distinguish "not yet loaded" from "load failed"
Flag any module-level singleton that uses `None` for both the uninitialized state
and the load-failed state. When initialization fails, a distinct sentinel value must
be set so subsequent calls short-circuit immediately without retrying, logging
repeated warnings, or masking the original failure.

---

## Correctness — Blocking

### All list endpoints must implement pagination
Flag any API endpoint that returns a collection without accepting `limit`/`offset`
(or cursor-based) parameters, or whose underlying query has no `LIMIT` clause.
Unbounded queries degrade performance and response size as data grows. Every list
endpoint must cap results and return pagination metadata.

### Public API identifiers must be consistent across the stack
Flag any case where the identifier used in a public API response, route path, or
client-facing field does not match the identifier used internally in the database,
store layer, or business logic for the same concept. Mismatches cause client errors
when the API response is used to construct subsequent requests.

### Correlation/trace IDs must be propagated to all outbound calls
Flag any outbound HTTP request (to external APIs, internal services, OAuth endpoints)
made within a request handler that does not forward the inbound request's correlation
or trace ID as a header. Distributed tracing requires end-to-end ID propagation.

### Async-trigger endpoints must return the correct status code
Flag any endpoint that fires asynchronous work (returns immediately while processing
continues in the background) that returns `200 OK` instead of `202 Accepted`. When
a single endpoint handles both synchronous and asynchronous paths (e.g., dry-run vs.
real run), each path must return the semantically correct status code.

### Concurrent resource access must use per-resource lock keys
Flag any lock whose key is scoped too broadly — e.g., a per-project lock used to
serialize operations that should be able to run concurrently per sub-resource
(workspace, tenant, file). A too-broad lock key causes concurrent operations to
silently no-op while the API reports success for all of them.

### Lock keys must be consistent across all code paths for the same resource
Flag any distributed or advisory lock where the key string is constructed inline
(via f-string or concatenation) at more than one call site for the same logical
resource. If an API trigger endpoint and a connector self-acquire path construct
the key differently — even with the same intended semantics — they take different
locks, allowing concurrent execution and seq/log corruption. All lock key construction
for a given resource must be centralised in a single shared helper or constant.

### Composite scoring functions must apply all signals consistently
Flag any multi-pass scoring or ranking function where a refinement pass recomputes
scores without applying all the signals used in the initial pass. Omitting a signal
in a later pass produces different composite scores and inconsistent winner selection.

### Re-upload or re-create operations must clear stale dependent state
Flag any upsert or re-create path that preserves linked/derived metadata rows from
a previous version of the record when those rows are no longer valid. Stale metadata
can corrupt downstream logic that depends on the linked state being current.

### Dependent operation results must be explicitly checked, not assumed successful
Flag any call to a dependency (another service, connector, or subsystem) whose return
value is not inspected before proceeding. If the dependency can return a no-op or
partial result (e.g., lock contention causing a silent skip), the caller must detect
and handle that case rather than assuming success.

### New identifiers must follow the project's ID derivation convention
Flag any new entity that generates IDs using a random UUID (`uuid4`) when a stable
natural key exists that could be used for deterministic derivation (`uuid5`).
Random IDs make upserts non-idempotent. Use `uuid4` only for entities that
genuinely have no natural key.

---

## Performance — Recommended

### Background index or sync operations must not block the event loop
Flag any background task (detached from the request lifecycle) that performs
CPU-bound work (embedding generation, fuzzy matching, serialization) or synchronous
I/O inside an async function on the main event loop. Offload to a thread pool or
subprocess.

---

## Type Safety — Blocking

### All functions must have explicit return type annotations
Flag any function definition (including methods, class methods, static methods, and
decorated functions) that is missing a return type annotation. This includes
`-> None`, `-> Iterator[T]`, `-> AsyncIterator[T]`, and generator functions. Apply
to all new and modified functions in the diff.

---

## Build — Blocking

### Dependency version constraints must be bounded or exact
Flag any new dependency added to a package manifest (`pyproject.toml`,
`requirements.txt`, `package.json`, etc.) using an unbounded lower-bound constraint
(`>=`, `>`). Use compatible-release (`^`, `~=`) or exact (`==`) constraints so
breaking major-version releases cannot land silently in CI.

### CI tooling must install all required dependency groups
Flag any CI configuration or test runner setup that installs a subset of dependency
groups but then invokes tools defined in omitted groups. Every tool invoked in CI
must be present in the installed dependency set.

---

## Recommended Improvements

### Don't access private methods or attributes on throwaway instances
Flag any pattern that instantiates an object solely to call a private method or
access a private attribute (prefixed with `_`), then discards the instance. Private
members are not part of the public contract. Expose a classmethod, factory, or
public initialization method instead.

### HTTP exceptions should be raised from route handlers, not from helper functions
Flag any non-handler function (utility, store, resolver, builder) that raises an
HTTP framework exception (`HTTPException`, `abort()`, etc.) directly. HTTP concerns
belong in the route handler layer. Helpers should return typed error values or
`None`; the handler decides the HTTP response.

### Best-effort operations should catch broadly and continue
Flag any operation explicitly documented as best-effort or non-fatal (e.g., search
index sync, cache warm, telemetry) that only suppresses a narrow exception subclass.
If the intent is "never abort the caller," the exception handler must be broad enough
to cover all realistic failure modes, with a log for each suppressed error.

### Retry logic must handle all valid formats of rate-limit headers
Flag any retry implementation that parses a rate-limit or backoff header (e.g.,
`Retry-After`) using a strict type conversion (`int()`, `float()`) without a
try/except fallback. HTTP specs allow multiple formats for these headers; a parse
failure should fall back to a safe default delay, not abort the operation.

### Backoff/cadence state must only advance when work was actually performed
Flag any adaptive scheduling or backoff implementation that updates the "next run"
timestamp even when the operation was skipped because it wasn't due. Advancing the
schedule on a skip progressively starves the operation from running.

### Sequence number generation must handle zero as a valid existing value
Flag any "next sequence number" implementation that uses a truthiness check (`val or
default`) to handle a missing value, where `0` is a valid stored value. `0 or default`
evaluates to `default`, causing the second sequence value to collide with the first.
Use an explicit `None` check instead.
