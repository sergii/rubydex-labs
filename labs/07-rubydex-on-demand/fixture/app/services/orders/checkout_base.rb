module Orders
  class CheckoutBase
    def initialize(order, payment_gateway: Payments::Gateway.new)
      @order = order
      @payment_gateway = payment_gateway
    end

    def finalize
      payment_gateway.capture(order)
    end

    private

    attr_reader :order, :payment_gateway
  end
end
