module Payments
  class Gateway
    private

    def after_capture(order, result)
      Ledger.record_capture(order.id, result.id)
      Orders::Confirm.call(order.id)
      Payments::AuditTrail.record(order.id, result.id)
    end
  end
end
