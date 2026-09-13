module Payments
  class ReconcileWebhook
    def self.call(payload)
      order = Order.find(payload.fetch(:order_id))
      provider_capture_id = payload.fetch(:provider_capture_id)

      Payments::Ledger.reconcile_capture!(
        order_id: order.id,
        provider_capture_id: provider_capture_id
      )

      Orders::Confirm.call(order, provider_capture_id: provider_capture_id)
    end
  end
end
