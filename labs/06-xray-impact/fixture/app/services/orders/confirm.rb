module Orders
  class Confirm
    def self.call(order, provider_capture_id:)
      order.mark_paid!(provider_capture_id: provider_capture_id)
      Notifications::PaymentReceiptJob.perform_later(order.id)
      order
    end
  end
end
