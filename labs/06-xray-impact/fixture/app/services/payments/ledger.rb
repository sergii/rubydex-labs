module Payments
  class Ledger
    def self.record_capture!(order_id:, provider_capture_id:)
      raise NotImplementedError
    end

    def self.reconcile_capture!(order_id:, provider_capture_id:)
      raise NotImplementedError
    end
  end
end
