module Payments
  class ProviderGateway
    def charge(order)
      result = provider.charge(order)
      after_capture(order, result)
      result
    end

    alias_method :capture, :charge

    private

    def after_capture(_order, _result)
      # extension hook
    end

    def provider
      raise NotImplementedError
    end
  end
end
