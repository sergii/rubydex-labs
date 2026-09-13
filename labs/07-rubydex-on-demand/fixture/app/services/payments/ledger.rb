module Payments
  class Ledger
    def self.record_capture(order_id, provider_payment_id)
      [order_id, provider_payment_id]
    end
  end
end
