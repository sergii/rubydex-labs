module Inventory
  class ReservationSyncJob < ApplicationJob
    def self.reservation_class
      Inventory::Reservation
    end

    def perform(reservation_id)
      Inventory::Reservation.find(reservation_id)
    end
  end
end
