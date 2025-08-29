
# Meeting Calculator Bot Sequence Diagram (Polling Email Server)

```mermaid
sequenceDiagram
    participant Bot
    participant EmailServer
    participant Organizer
    participant DB
    participant Participan

    loop Periodically
        Bot->>EmailServer: Poll for new meeting invite emails (IMAP)
        EmailServer-->>Bot: Return new emails
    end
    Bot->>Bot: Parse meeting details (date, time, participants, roles)
    Bot->>DB: Lookup roles and wages
    DB-->>Bot: Return wage data
    Bot->>Bot: Calculate meeting cost
    Bot->>EmailServer: Send cost summary email to organizer
    EmailServer-->>Organizer: Deliver cost summary
```
