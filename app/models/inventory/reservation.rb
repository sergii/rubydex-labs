module Inventory
  class Reservation < ApplicationRecord
    self.table_name = "inventory_reservations"
  end
end
