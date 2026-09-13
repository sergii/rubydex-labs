module Payments
  class AuditTrail
    def self.record(order_id, provider_payment_id)
      Reporting::PaymentEvents.publish(order_id, provider_payment_id)
    end
  end
end
