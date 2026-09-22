# Phase 03 — Refresh Figures Runtime Fix

## Change ID
FIX-REFRESH-001

## Current behavior
The native Dashboard `Refresh all figures` action attempted to create `FunctionTask("dashboard_figures", function, True)` even though `FunctionTask.__init__` accepts only `(key, function)`.

## Defect
Clicking **Refresh all figures** raises:

`TypeError: FunctionTask.__init__() takes 3 positional arguments but 4 were given`

## Required behavior
Run `refresh_dashboard_figures(full_rebuild=True)` outside the managed download queue without blocking the GUI and without violating the `FunctionTask` constructor contract.

## Implementation
Wrap the one-argument backend call in a zero-argument callable:

`FunctionTask("dashboard_figures", lambda: function(True))`

## Regression protection
Added an AST-based source-contract test that rejects any `FunctionTask` call with more than two positional arguments.
