# Agent Roles

This document outlines the roles and responsibilities of the agents involved in the development of the Xynetech Macro Agent project.

## 1. Macro Analyst Agent
- **Description**: Analyzes macroeconomic indicators and Federal Reserve announcements to gauge market sentiment and identify trends.
- **Responsibilities**:
  - Fetching and parsing Fed announcements and press releases.
  - Determining positive/negative sentiment and key policy directions (e.g., hawkish vs. dovish).
  - Summarizing macroeconomic conditions for the allocation logic.

## 2. Code Writer Agent
- **Description**: Translates strategies and analysis into executable code and implements the target logic.
- **Responsibilities**:
  - Developing and maintaining core application modules (`fed_watcher.py`, `sector_allocator.py`, `portfolio_tracker.py`).
  - Implementing LLM integrations for processing unstructured text and generating sector weights.
  - Ensuring clean code practices, proper error handling, and modular structure.

## 3. Portfolio Tester Agent
- **Description**: Validates the performance, accuracy, and reliability of the macro-driven portfolio strategies.
- **Responsibilities**:
  - Simulating historical and live stock token trades based on sector weights.
  - Calculating and monitoring key performance metrics (e.g., returns, Sharpe ratio, drawdowns).
  - Writing test suites and validation scripts to verify sector allocation rules and portfolio math.
