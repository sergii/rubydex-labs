class Order
  attr_reader :id, :amount_cents

  def self.find(id)
    raise NotImplementedError
  end

  def mark_payment_pending!
    raise NotImplementedError
  end

  def mark_paid!(provider_capture_id:)
    raise NotImplementedError
  end
end
