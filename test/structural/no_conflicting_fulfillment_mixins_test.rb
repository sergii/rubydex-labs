require "test_helper"

class NoConflictingFulfillmentMixinsTest < ActiveSupport::TestCase
  test "no class has both fulfillment implementations in its ancestor chain" do
    Rails.application.eager_load!

    offenders = ObjectSpace.each_object(Class).select do |klass|
      ancestors = klass.ancestors
      ancestors.include?(LegacyFulfillment) && ancestors.include?(ModernFulfillment)
    end

    assert_empty(
      offenders,
      "Classes with conflicting fulfillment mixins: #{offenders.map(&:name).compact.sort.join(', ')}",
    )
  end
end
