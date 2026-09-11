module Inventory
  class Allocator
    def reservation_class
      Reservation
    end

    def build(attributes = {})
      Reservation.new(attributes)
    end
  end
end
