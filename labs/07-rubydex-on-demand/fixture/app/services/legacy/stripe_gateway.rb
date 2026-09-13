module Legacy
  class StripeGateway
    # Historical adapter. The words capture, ledger, checkout and Stripe appear here
    # but this class is not referenced by the active checkout flow.
    def capture(order)
      "legacy-#{order.id}"
    end
  end
end
