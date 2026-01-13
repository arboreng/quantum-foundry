# RFC-0001: Shor's Algorithm From Scratch

Status: Draft

## Vision

Educational quantum computing reference implementation.

## Why This Should Exist

A focused educational reference that demonstrates production-quality
engineering rather than a toy implementation.

## Prior Art

-   Survey existing implementations
-   Identify gaps
-   Define Arbor Engineering differentiators

## Architecture

-   Core components
-   Data flow
-   Extension points

## Technology Choices

Python, Qiskit

## Milestones

-   [x] v0.1: Skeleton
-   [x] v0.2: Core implementation
-   [ ] v0.5: Feature complete
-   [ ] v0.8: Documentation
-   [ ] v1.0: Public release

## Seed GitHub Issues

-   Project scaffolding
-   CI/CD
-   Tests
-   Benchmarks
-   Documentation

## README Outline

-   Motivation
-   Quick Start
-   Architecture
-   Examples
-   Benchmarks
-   Roadmap
-   Contributing

## Launch Plan

-   Technical blog
-   LinkedIn article
-   Hacker News
-   Reddit
-   Conference/demo

## Stretch Goals

Classical math, QFT, modular exponentiation, order finding, benchmarks

## Explicit Non-goals (v0.2)

So reviewers see these as deliberately deferred, not overlooked:

-   No hardware execution
-   No elementary-gate synthesis of the modular-multiplication oracle
-   No fault tolerance
-   No optimization passes beyond Qiskit's default `transpile()`
-   No custom transpiler/hardware-aware layout work
-   No distributed simulation
-   No GPU acceleration
