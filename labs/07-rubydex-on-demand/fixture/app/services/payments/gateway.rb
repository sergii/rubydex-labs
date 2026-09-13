module Payments
  class Gateway < ProviderGateway
    private

    def provider
      StripeProvider.new
    end
  end
end
