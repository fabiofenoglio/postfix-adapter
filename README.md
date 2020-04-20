# postfix-adapter

Django-based application that exposes a local postfix mail delivery status as REST API.

Works by tail-parsing logs and extracting info with priority-based multiple chained regex extractors.

## Exposed endpoints:
`<host>/postfix-adapter/mail-status/?format=json`

`<host>/postfix-adapter/mail-status/<queue_id>/?format=json`

Response format:

```
  {
    "queue_id": "514F5C5214",
    "message_id": "<514F5C5214.86.15873823645123@hostname>",
    "status": "sent",
    "message": "250 2.0.0 OK  15873853211 q196si663832dws.18 - relayed by smtp",
    "insert_date": "2020-04-20T13:32:41.439470+02:00",
    "update_date": "2020-04-20T13:32:45.291487+02:00",
    "version": 6
  }
```
