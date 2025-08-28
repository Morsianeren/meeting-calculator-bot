# System Architecture

```mermaid
flowchart TD
    subgraph Email Handling
        IMAP[IMAP Email Fetch]
        SMTP[SMTP Email Send]
    end
    subgraph Meeting Processing
        ParseInvite[Parse Meeting Invitation]
        FilterSender[Filter @deif.com]
        ExtractDetails[Extract Details]
        CostCalc[Calculate Meeting Cost]
        Feedback[Feedback Survey]
    end
    subgraph Data Storage
        TempDB[Temporary Meeting DB]
        MainDB[Main Meeting DB]
    end
    IMAP --> ParseInvite
    ParseInvite --> FilterSender
    FilterSender --> ExtractDetails
    ExtractDetails --> CostCalc
    CostCalc --> SMTP
    ExtractDetails --> TempDB
    Feedback --> TempDB
    TempDB --> MainDB
    SMTP --> Feedback
```
