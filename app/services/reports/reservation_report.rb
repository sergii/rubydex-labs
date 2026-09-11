module Reports
  class ReservationReport
    TITLE = "Inventory Reservation report"
    LEGACY_EXPORT_KEY = "Inventory::Reservation"

    def self.description
      "Reservation activity across inventory and admin systems"
    end
  end
end
