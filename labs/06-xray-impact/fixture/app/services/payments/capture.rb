module Payments
  class Capture
    def self.call(order_id)
      order = Order.find(order_id)
      idempotency_key = "order:#{order.id}:capture"

      result = Payments::StripeGateway.capture(
        order_id: order.id,
        amount_cents: order.amount_cents,
        idempotency_key: idempotency_key
      )

      Payments::Ledger.record_capture!(
        order_id: order.id,
        provider_capture_id: result.id
      )

      Orders::Confirm.call(order, provider_capture_id: result.id)
      result
    end
  end
end
