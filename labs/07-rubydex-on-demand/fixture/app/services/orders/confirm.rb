module Orders
  class Confirm
    def self.call(order_id)
      OrderRepository.mark_paid(order_id)
      Notifications::PaymentReceiptJob.perform_later(order_id)
    end
  end
end
