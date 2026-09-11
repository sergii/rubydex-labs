module Warehouse
  class StockMoveProcessor < BaseProcessor
    include ModernFulfillment

    def call
      fulfillment_strategy
    end
  end
end
