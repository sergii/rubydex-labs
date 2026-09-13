module Payments
  class CaptureJob < ApplicationJob
    queue_as :payments

    retry_on Payments::ProviderTimeout,
      wait: :polynomially_longer,
      attempts: 5

    discard_on Payments::CardDeclined

    def perform(order_id)
      Payments::Capture.call(order_id)
    end
  end
end
