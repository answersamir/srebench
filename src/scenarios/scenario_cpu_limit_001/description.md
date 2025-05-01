# Incident Description: Slow Checkout and Payment Errors

Users began reporting intermittent failures and significant delays when attempting to complete purchases via the checkout process. The frontend application became sluggish during payment submission.

Initial monitoring alerts triggered for high p99 latency on the `checkoutservice`'s gRPC calls, specifically targeting the `paymentservice`. Simultaneously, alerts indicated elevated error rates for payment processing requests originating from the `checkoutservice`.

Further investigation revealed that the `paymentservice` itself was exhibiting high CPU utilization, consistently hitting its configured limit, and showing increased request latency. Dependent services, primarily `checkoutservice`, were consequently impacted, leading to the observed user-facing issues.