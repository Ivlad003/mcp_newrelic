---
description: Investigate a production incident using New Relic data — correlates errors, latency, deployments, and infrastructure
---

# New Relic Incident Investigation

Investigate a production incident by correlating multiple New Relic signals.

## Instructions

Use the `newrelic-investigator` agent to handle this investigation. Pass along any context the user provided (service name, time range, symptoms).

The agent will:
1. Check active alerts
2. Query error rates and latency
3. Check recent deployments
4. Review infrastructure metrics
5. Correlate signals and identify probable cause
6. Present a structured incident summary
