module Orders
  class Processor
    def reservation_class
      Inventory::Reservation
    end

    def reservation_for(order_id)
      Inventory::Reservation.find_by(order_id: order_id)
    end
  end
end
