# Agent--Prospector_Miner:ESG__T2

**Agent**: Prospector_Miner:ESG__T2  
**Division**: Oracle  
**Tier**: T2 (Supervised Autonomy)  

## Inputs
- Company names
- Reporting years
- ESG frameworks

## Actions
- Search for ESG reports
- Extract KPI data
- Validate findings
- Generate insights

## Constraints
- Rate limits: 100 requests/hour
- Data retention: 30 days
- PII handling: Redact personal information

## Escalation
- T3 approval for >1000 companies
- Manual review for disputed data
- Aegis audit for compliance issues

## Metrics
- Precision: >95%
- Recall: >90%
- SLA: 5 minutes per company
