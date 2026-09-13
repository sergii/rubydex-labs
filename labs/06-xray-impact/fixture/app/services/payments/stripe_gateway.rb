module Payments
  class StripeGateway
    CaptureResult = Data.define(:id)

    def self.capture(order_id:, amount_cents:, idempotency_key:)
      raise NotImplementedError
    end
  end
end
