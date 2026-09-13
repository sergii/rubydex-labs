class StripeWebhooksController
  def create
    Payments::ReconcileWebhook.call(params)
    head :ok
  end
end
