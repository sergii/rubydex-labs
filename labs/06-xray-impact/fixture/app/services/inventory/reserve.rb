module Inventory
  class Reserve
    def self.call(order)
      new(order).call
    end

    def initialize(order)
      @order = order
    end

    def call
      true
    end
  end
end
