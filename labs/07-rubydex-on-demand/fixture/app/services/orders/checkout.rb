module Orders
  class Checkout < CheckoutBase
    def call
      validate_order!
      finalize
    end

    private

    def validate_order!
      true
    end
  end
end
