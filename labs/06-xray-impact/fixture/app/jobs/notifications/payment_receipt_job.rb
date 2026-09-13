module Notifications
  class PaymentReceiptJob < ApplicationJob
    queue_as :mailers

    def perform(order_id)
      true
    end
  end
end
