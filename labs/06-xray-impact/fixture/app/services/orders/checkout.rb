module Orders
  class Checkout
    def self.call(order)
      new(order).call
    end

    def initialize(order)
      @order = order
    end

    def call
      Inventory::Reserve.call(@order)
      @order.mark_payment_pending!
      Payments::CaptureJob.perform_later(@order.id)
      @order
    end
  end
end
