# gossipbot

This posts Silicon Beach gossip to slack.

Program Flow:

  * Amazon SES
    * Lambda Handler
      * Slack

## Configuration

  * Subscribe SES to appropriate mailing list, write messages to S3
  * Set `SLACK_WEBHOOK` envvar on lambda function
