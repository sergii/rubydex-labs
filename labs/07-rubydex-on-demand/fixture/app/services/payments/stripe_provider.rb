module Payments
  class StripeProvider
    Result = Struct.new(:id)

    def charge(order)
      Result.new("pi_#{order.id}")
    end
  end
end
